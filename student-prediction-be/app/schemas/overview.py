from typing import Literal, Optional

from pydantic import BaseModel


class RecentSessionItem(BaseModel):
    id: str
    type: Literal["chat", "batch", "form"]
    label: str
    createdAt: str
    status: Literal["in_progress", "done", "failed"]
    studentCount: Optional[int] = None
    riskLevel: Optional[Literal["low", "medium", "high"]] = None


class RecentStudentItem(BaseModel):
    id: str
    name: str
    studentId: str
    statusLabel: Literal["Dropout", "Graduate"]
    riskLevel: Literal["low", "medium", "high"]
    assessedAt: str


class OverviewResponse(BaseModel):
    totalAssessed: int
    lowRisk: int
    mediumRisk: int
    highRisk: int
    recentSessions: list[RecentSessionItem]
    recentStudents: list[RecentStudentItem]
