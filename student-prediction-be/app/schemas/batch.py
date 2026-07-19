from pydantic import BaseModel
from typing import Literal, Optional


class RiskAssessmentSchema(BaseModel):
    statusLabel: Literal["Dropout", "Graduate"]  # "Enrolled" added in phase 2
    riskLevel: Literal["low", "medium", "high"]
    riskProb: float  # 0.0–1.0
    recommendation: str
    factors: list[str]


class StudentSchema(BaseModel):
    id: str
    name: str
    studentId: str
    reviewed: bool = False
    assessment: RiskAssessmentSchema


class BatchSubmitResponse(BaseModel):
    jobId: str


class BatchJobResponse(BaseModel):
    status: Literal["processing", "done", "failed"]
    progress: int  # 0–100
    results: Optional[list[StudentSchema]] = None
    error: Optional[str] = None
