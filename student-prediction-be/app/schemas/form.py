from pydantic import BaseModel
from typing import Any, Literal
from .batch import RiskAssessmentSchema


class FormRequest(BaseModel):
    predictionType: Literal["ml", "rule_based"]
    fields: dict[str, Any]
    name: str | None = None
    studentId: str | None = None


class FormResultResponse(BaseModel):
    conversationId: str
    data: RiskAssessmentSchema
