"""Shared schema for assessment results and batch uploads."""

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


DataSource = Literal["student_dropout_and_success", "student_dropout"]
PredictionType = Literal["ml", "rule_based"]
PredictedStatus = Literal["Dropout", "No Dropout", "Graduate"]


class RiskAssessmentSchema(BaseModel):
    # Standard contract of the two-source / two-solution integration.
    dataSource: DataSource
    solutionType: PredictionType
    prediction: Literal["Dropout", "No Dropout"]
    riskScore: float = Field(ge=0.0, le=1.0)
    riskLevel: Literal["low", "medium", "high"]
    riskFactors: list[str]
    recommendations: list[str]
    scoreType: Literal["probability", "normalized_rule_score"]

    # Fields kept compatible with the older UI and docs.
    statusLabel: PredictedStatus
    riskProb: float = Field(ge=0.0, le=1.0)
    recommendation: str
    factors: list[str]


class StudentSchema(BaseModel):
    id: str
    name: str
    studentId: str
    reviewed: bool = False
    assessment: RiskAssessmentSchema
    assessed_at: str = ""
    features: Optional[dict[str, Any]] = None


class BatchSubmitResponse(BaseModel):
    jobId: str


class BatchSyncResponse(BaseModel):
    results: list[StudentSchema]


class BatchJobResponse(BaseModel):
    status: Literal["processing", "done", "failed"]
    progress: int = Field(ge=0, le=100)
    results: Optional[list[StudentSchema]] = None
    error: Optional[str] = None
