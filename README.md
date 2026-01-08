# Behaviour-Aware Federated Wind Power Forecasting System (demo)

A full-stack wind turbine power forecasting application demonstrating modern microservices architecture with ML integration:

**React Frontend** → **ASP.NET Core 8.0 API (C#)** → **FastAPI Service (Python)** → **PyTorch LSTM Models (.h5)**

> **Note**: This is a demonstration project. All turbine data, locations, and predictions are synthetically generated. The LSTM models use cluster-based behavior patterns to simulate realistic wind power forecasting scenarios.



## Features

✅ **Real-time Forecasting**: Generate 24-hour power predictions for any turbine  
✅ **Interactive Map**: Visualize 400+ wind turbines across Denmark (Zealand Island)  
✅ **Cluster-based Models**: 6 distinct LSTM models for different turbine behavioral patterns  

## Usage

1. **View Turbines**: The map displays 400+ turbines across Denmark's Zealand Island
2. **Select Turbine**: Click any turbine marker to see details (ID, Cluster, Capacity)
3. **Request Forecast**: Click "Request 24h Forecast" button
4. **View Results**: A line chart shows hourly power predictions for the next 24 hours
5. **Analyze Patterns**: Different clusters show distinct behavioral patterns

## Demo
![demo](./demo/demo.gif)


---

## Cluster-based Model Architecture

The system uses **6 pre-trained PyTorch LSTM models**, each optimized for different turbine behavioral patterns:

| Cluster | Turbines | Characteristics |
|---------|----------|-----------------|
| **0** | 4 | High power output, high volatility, minimal downtime |
| **2** | 4 | Ramp-dominated, strong power changes |
| **3** | 251 | Stable baseline, most reliable |
| **4** | 76 | Mid-risk, lower output, frequent downtime |
| **5** | 6 | Promising, moderate volatility |
| **6** | 10 | Mildly unstable, frequent ramp-ups |

### Model Details
- **Architecture**: LSTM (input_size=9, hidden_size=128, num_layers=1, output_size=3)
- **Input Features**: wind_speed, wind_dir_sin, wind_dir_cos, temperature, hour_sin, hour_cos, capacity, age, power_lag
- **Storage Format**: HDF5 files containing:
  - Model weights (PyTorch state_dict)
  - X scalers (per-turbine input normalization)
  - Y scalers (per-turbine output denormalization)
- **Output**: 24 hourly power predictions in MW

## Technical Details

### Data Flow
```
User clicks turbine
    ↓
React → POST /api/forecast
    ↓
C# Controller validates & looks up turbine
    ↓
C# Service → POST http://localhost:8000/predict
    ↓
Python loads LSTM model for cluster
    ↓
Model generates 24 predictions (normalized)
    ↓
Y scaler denormalizes to actual kW → MW
    ↓
JSON response flows back through layers
    ↓
React chart displays results
```

### Error Handling
- **Turbine not found**: Returns 404
- **Python service down**: Returns 502 with error message

---

## Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | React | 18+ |
| Build Tool | Vite | 5+ |
| Mapping | Leaflet | 1.9+ |
| Charts | Chart.js | 4+ |
| API Gateway | ASP.NET Core | 8.0 |
| Language | C# | 12 |
| ML Service | FastAPI | 0.104+ |
| ML Framework | PyTorch | 2.1+ |
| Data Format | HDF5 (h5py) | 3.10+ |
| HTTP Client | HttpClient | .NET 8.0 |

---


---

## Project Structure

```
turbine_forecasting/
├── src/                          # C# ASP.NET Core 8.0 API
│   ├── Controllers/
│   │   ├── TurbinesController.cs    # GET turbine list/details
│   │   └── ForecastController.cs    # POST forecast requests
│   ├── Services/
│   │   └── ForecastService.cs       # HttpClient to Python service
│   ├── Models/
│   │   ├── Turbine.cs               # Turbine data model 
│   │   └── ForecastRequest.cs       # Request DTO
│   ├── Program.cs                   # Application entry and DI configuration
│   ├── appsettings.json            # Configuration (Python service URL)
│   └── TurbineForecast.Api.csproj  # .NET project file
│
├── python_service/               # Python FastAPI ML Service
│   ├── main.py                   # FastAPI app with /predict endpoint
│   ├── models.py                 # Model loading, MinMaxScaler implementation
│   ├── prediction.py             # LSTM inference logic with cluster behavior
│   ├── cluster_config.py         # Cluster behavioral profiles
│   ├── generate_turbines.py      # Utility to generate turbine data
│   └── requirements.txt          # Python dependencies
│
├── frontend/                     # React + Vite Frontend
│   ├── src/
│   │   ├── App.jsx               # Main application component
│   │   ├── components/
│   │   │   ├── MapView.jsx       # Leaflet map with turbine markers
│   │   │   └── ForecastChart.jsx # Chart.js line chart
│   │   └── main.jsx              # React entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js            # Vite configuration
│
├── models/                       # Pre-trained LSTM models
│   ├── full_model_cluster0.h5    # Cluster 0 model + scalers
│   ├── full_model_cluster2.h5    # Cluster 2 model + scalers
│   ├── full_model_cluster3.h5    # Cluster 3 model + scalers
│   ├── full_model_cluster4.h5    # Cluster 4 model + scalers
│   ├── full_model_cluster5.h5    # Cluster 5 model + scalers
│   └── full_model_cluster6.h5    # Cluster 6 model + scalers
│
├── data/
│   └── turbines.json             # 400+ turbine metadata
│
├── scripts/
│   └── dev.sh                    # Development startup script
│
└── README.md                     # This file
```

---

## API Endpoints

### C# ASP.NET Core API (Port 5000)

#### Turbines API
```http
GET /api/turbines
```
Returns all turbines with id, name, latitude, longitude, clusterId, capacity.

```http
GET /api/turbines/{id}
```
Returns details for a specific turbine.

#### Forecast API
```http
POST /api/forecast
Content-Type: application/json

{
  "turbineId": "570715000000125638",
  "startTime": "2024-01-15T00:00:00Z"
}
```

**Response:**
```json
{
  "turbineId": "570715000000125638",
  "clusterId": 0,
  "predictions": [
    { "hour": 0, "power": 1.234 },
    { "hour": 1, "power": 1.456 },
    ...
    { "hour": 23, "power": 0.987 }
  ]
}
```

### Python FastAPI Service (Port 8000)

#### Prediction Endpoint
```http
POST /predict
Content-Type: application/json

{
  "turbineId": "570715000000125638",
  "clusterId": 0,
  "capacity": 3.2,
  "startTime": "2024-01-15T00:00:00Z"
}
```

**Response:** Same format as C# API

#### Health Check
```http
GET /
```
Returns service status and available models.

---

## Getting Started

### Prerequisites
- **.NET 8.0 SDK** - [Download](https://dotnet.microsoft.com/download)
- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)

### Installation & Running

```bash
cd turbine_forecasting
chmod +x scripts/dev.sh
./scripts/dev.sh
```

This script starts all three services concurrently.

---

