from pydantic import BaseModel
from typing import Any
from .batch import DataSource, PredictionType, RiskAssessmentSchema


class FormRequest(BaseModel):
    dataSource: DataSource
    predictionType: PredictionType
    fields: dict[str, Any]
    name: str | None = None
    studentId: str | None = None


class FormResultResponse(BaseModel):
    conversationId: str
    data: RiskAssessmentSchema
