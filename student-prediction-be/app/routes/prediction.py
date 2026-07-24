"""Synchronous prediction API that does not depend on MongoDB or Gemini."""

from fastapi import APIRouter, HTTPException

from app.schemas.prediction import SinglePredictionRequest, SinglePredictionResponse
from app.services import risk_service


router = APIRouter()


@router.post("/predict/single", response_model=SinglePredictionResponse)
async def predict_single(request: SinglePredictionRequest) -> dict:
    """Predict a single student using one of the four experiment configurations."""
    try:
        return risk_service.assess(
            request.features,
            prediction_type=request.predictionType,
            data_source=request.dataSource,
        )
    except (ValueError, RuntimeError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
