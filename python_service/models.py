"""
PyTorch LSTM model definition and loading utilities.
"""
import os
from typing import Dict, Any, Tuple

import torch
import torch.nn as nn
import h5py
import numpy as np
from fastapi import HTTPException


class MinMaxScaler:
    """MinMaxScaler compatible with sklearn's MinMaxScaler loaded from HDF5."""
    
    def __init__(self, scale: np.ndarray, min_: np.ndarray):
        """
        Initialize scaler with parameters from sklearn's MinMaxScaler.
        
        Args:
            scale: Scale factor array
            min_: Minimum offset array
        """
        self.scale_ = scale
        self.min_ = min_
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        """Transform features by scaling to [0,1] range."""
        return X * self.scale_ + self.min_
    
    def inverse_transform(self, X: np.ndarray) -> np.ndarray:
        """Inverse transform to original scale."""
        return (X - self.min_) / self.scale_


class SimpleLSTM(nn.Module):
    """PyTorch LSTM model for wind power forecasting."""
    
    def __init__(self, input_size=9, hidden_size=128, num_layers=1, output_size=3):
        super(SimpleLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        # Model uses MLP_layers.0 for output
        self.fc = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        """
        Forward pass through the LSTM model.
        
        Args:
            x: Input tensor of shape (batch, seq_len, input_size)
            
        Returns:
            Predictions of shape (batch, output_size)
        """
        # x shape: (batch, seq_len, input_size)
        lstm_out, _ = self.lstm(x)
        # Use last timestep output
        last_output = lstm_out[:, -1, :]
        predictions = self.fc(last_output)
        return predictions


# Cache loaded models and scalers by clusterId for speed
# Structure: {cluster_id: (model, x_scalers, y_scalers)}
_models: Dict[int, Tuple[Any, Dict[str, MinMaxScaler], Dict[str, MinMaxScaler]]] = {}

# Use absolute path for models directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
AVAILABLE_CLUSTERS = {0, 2, 3, 4, 5, 6}  # Cluster 1 model file not available


def get_model(cluster_id: int) -> Tuple[Any, Dict[str, MinMaxScaler], Dict[str, MinMaxScaler]]:
    """
    Load PyTorch LSTM model from HDF5 file with weights and scalers.
    
    Args:
        cluster_id: Cluster identifier (0, 2, 3, 4, 5, 6)
        
    Returns:
        Tuple of (model, x_scalers, y_scalers) where:
        - model: Loaded PyTorch model in evaluation mode
        - x_scalers: Dict mapping turbine_id to input feature scaler
        - y_scalers: Dict mapping turbine_id to output scaler
        
    Raises:
        HTTPException: If cluster is unsupported or model loading fails
    """
    if cluster_id not in AVAILABLE_CLUSTERS:
        raise HTTPException(status_code=400, detail="Unsupported clusterId")
    if cluster_id in _models:
        return _models[cluster_id]

    # Load model from HDF5 format
    model_path = os.path.join(MODELS_DIR, f"full_model_cluster{cluster_id}.h5")
    
    if not os.path.exists(model_path):
        raise HTTPException(status_code=500, detail=f"Model file not found for cluster {cluster_id}")

    try:
        # Create model instance
        model = SimpleLSTM(input_size=9, hidden_size=128, num_layers=1, output_size=3)
        
        # Load from HDF5 format (trained model)
        with h5py.File(model_path, 'r') as f:
            state_dict = {}
            model_weights = f['model_weights']
            
            # Load LSTM weights
            state_dict['lstm.weight_ih_l0'] = torch.from_numpy(model_weights['lstm.weight_ih_l0'][:])
            state_dict['lstm.weight_hh_l0'] = torch.from_numpy(model_weights['lstm.weight_hh_l0'][:])
            state_dict['lstm.bias_ih_l0'] = torch.from_numpy(model_weights['lstm.bias_ih_l0'][:])
            state_dict['lstm.bias_hh_l0'] = torch.from_numpy(model_weights['lstm.bias_hh_l0'][:])
            
            # Load MLP output layer weights
            state_dict['fc.weight'] = torch.from_numpy(model_weights['MLP_layers.0.weight'][:])
            state_dict['fc.bias'] = torch.from_numpy(model_weights['MLP_layers.0.bias'][:])
            
            model.load_state_dict(state_dict)
            
            # Load x_scaler and y_scaler for each turbine
            x_scalers = {}
            y_scalers = {}
            
            if 'x_scaler' in f:
                for turbine_id in f['x_scaler'].keys():
                    scaler_data = f['x_scaler'][turbine_id]
                    x_scalers[turbine_id] = MinMaxScaler(
                        scale=scaler_data['scale_'][:],
                        min_=scaler_data['min_'][:]
                    )
            
            if 'y_scaler' in f:
                for turbine_id in f['y_scaler'].keys():
                    scaler_data = f['y_scaler'][turbine_id]
                    y_scalers[turbine_id] = MinMaxScaler(
                        scale=scaler_data['scale_'][:],
                        min_=scaler_data['min_'][:]
                    )
        
        model.eval()
        _models[cluster_id] = (model, x_scalers, y_scalers)
        return model, x_scalers, y_scalers
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")
