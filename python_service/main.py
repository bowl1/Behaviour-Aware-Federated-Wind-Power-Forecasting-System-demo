"""
FastAPI application for wind power forecasting inference service.
Provides REST API endpoints for turbine power predictions.
"""
import datetime as dt
import json
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from models import get_model
from prediction import predict_24h


app = FastAPI(title="Wind Power Inference Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


class ForecastRequest(BaseModel):
    """Frontend forecast request model."""
    turbineId: str
    startTime: str  # ISO 8601


class Turbine(BaseModel):
    """Turbine model returned to frontend."""
    id: str
    name: str
    latitude: float
    longitude: float
    clusterId: int
    capacity: float = 3.0


_turbines_cache: List[Turbine] | None = None
_turbines_mtime: float | None = None


def load_turbines() -> List[Turbine]:
    """Load and cache turbines from data/turbines.json."""
    global _turbines_cache, _turbines_mtime

    data_path = str(Path(__file__).resolve().parents[1] / "data" / "turbines.json")
    if not Path(data_path).exists():
        raise HTTPException(status_code=500, detail=f"turbines.json not found: {data_path}")

    current_mtime = Path(data_path).stat().st_mtime
    if _turbines_cache is not None and _turbines_mtime == current_mtime:
        return _turbines_cache

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    _turbines_cache = sorted(
        [
            Turbine(
                id=item["turbineId"],
                name=item["turbineId"],
                latitude=item["latitude"],
                longitude=item["longitude"],
                clusterId=item["clusterId"],
                capacity=item.get("capacity", 3.0),
            )
            for item in data.get("turbines", [])
        ],
        key=lambda t: t.id,
    )
    _turbines_mtime = current_mtime
    return _turbines_cache


def run_prediction(
    turbine_id: str,
    cluster_id: int,
    capacity: float,
    start_time: str,
) -> PredictResponse:
    """Shared inference logic for /predict and /api/forecast."""
    try:
        _ = dt.datetime.fromisoformat(start_time.replace("Z", "+00:00"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid startTime format")

    model, x_scalers, y_scalers = get_model(cluster_id)
    values = predict_24h(
        model,
        x_scalers=x_scalers,
        y_scalers=y_scalers,
        capacity_mw=capacity,
        cluster_id=cluster_id,
        turbine_id=turbine_id,
    )
    predictions = [
        PredictionPoint(hour=i, power=round(float(values[i]), 3))
        for i in range(24)
    ]
    return PredictResponse(
        turbineId=turbine_id,
        clusterId=cluster_id,
        predictions=predictions,
    )


@app.get("/")
def health():
    """Basic health endpoint."""
    return {"status": "ok", "service": "wind-power-inference"}


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
    return run_prediction(
        turbine_id=req.turbineId,
        cluster_id=req.clusterId,
        capacity=req.capacity,
        start_time=req.startTime,
    )


@app.get("/api/turbines", response_model=List[Turbine])
def get_all_turbines():
    """Return all turbines for frontend map display."""
    return load_turbines()


@app.get("/api/turbines/{turbine_id}", response_model=Turbine)
def get_turbine_by_id(turbine_id: str):
    """Return one turbine by id."""
    turbine = next(
        (t for t in load_turbines() if t.id.lower() == turbine_id.lower()),
        None,
    )
    if turbine is None:
        raise HTTPException(status_code=404, detail="Turbine not found")
    return turbine


@app.post("/api/forecast", response_model=PredictResponse)
def forecast(req: ForecastRequest):

    turbine = next(
        (t for t in load_turbines() if t.id.lower() == req.turbineId.lower()),
        None,
    )
    if turbine is None:
        raise HTTPException(status_code=404, detail="Turbine not found")

    return run_prediction(
        turbine_id=turbine.id,
        cluster_id=turbine.clusterId,
        capacity=turbine.capacity,
        start_time=req.startTime,
    )


# To run: uvicorn main:app --reload --port 8000
