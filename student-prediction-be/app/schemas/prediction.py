"""Schema for the synchronous single-student prediction API."""

from typing import Any

from pydantic import BaseModel

from app.schemas.batch import DataSource, PredictionType, RiskAssessmentSchema


class SinglePredictionRequest(BaseModel):
    dataSource: DataSource
    predictionType: PredictionType
    features: dict[str, Any]


class SinglePredictionResponse(RiskAssessmentSchema):
    pass
