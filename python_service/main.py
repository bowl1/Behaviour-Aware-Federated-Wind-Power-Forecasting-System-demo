"""
FastAPI application for wind power forecasting inference service.
Provides REST API endpoints for turbine power predictions.
"""
import datetime as dt
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from models import get_model
from prediction import predict_24h


app = FastAPI(title="Wind Power Inference Service")


class PredictRequest(BaseModel):
    """Request model for power prediction."""
    turbineId: str
    clusterId: int
    startTime: str  # ISO 8601
    capacity: float = 3.0  # Turbine capacity in MW, default 3.0


class PredictionPoint(BaseModel):
    """Single hour prediction point."""
    hour: int
    power: float


class PredictResponse(BaseModel):
    """Response model containing 24-hour predictions."""
    turbineId: str
    clusterId: int
    predictions: List[PredictionPoint]


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    """
    Generate 24-hour power predictions for a wind turbine.
    
    Args:
        req: Prediction request containing turbine ID, cluster ID, start time, and capacity
        
    Returns:
        24 hourly power predictions with cluster-specific behavior
        
    Raises:
        HTTPException: If request validation fails or model loading fails
    """
    # Parse time (not used by the simple demo logic)
    try:
        _ = dt.datetime.fromisoformat(req.startTime.replace("Z", "+00:00"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid startTime format")

    # Load model and scalers based on cluster
    model, x_scalers, y_scalers = get_model(req.clusterId)

    # Predict next 24 hours with cluster-specific behavior and turbine capacity
    values = predict_24h(
        model,
        x_scalers=x_scalers,
        y_scalers=y_scalers,
        capacity_mw=req.capacity,
        cluster_id=req.clusterId,
        turbine_id=req.turbineId
    )
    predictions = [
        PredictionPoint(hour=i, power=round(float(values[i]), 3))
        for i in range(24)
    ]

    return PredictResponse(
        turbineId=req.turbineId,
        clusterId=req.clusterId,
        predictions=predictions,
    )


# To run: uvicorn main:app --reload
