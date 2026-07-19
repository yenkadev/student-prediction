from typing import Literal, Optional
from pydantic import BaseModel
from app.schemas.batch import RiskAssessmentSchema


class AcademicFeatures(BaseModel):
    GPA: Optional[float] = None
    Attendance_Rate: Optional[float] = None
    Stress_Index: Optional[float] = None
    Study_Hours_per_Day: Optional[float] = None
    Assignment_Delay_Days: Optional[float] = None
    Internet_Access: Optional[str] = None
    Part_Time_Job: Optional[str] = None
    Gender: Optional[str] = None
    Scholarship: Optional[str] = None
    Semester: Optional[str] = None
    Department: Optional[str] = None
    Parental_Education: Optional[str] = None
    Age: Optional[float] = None
    Family_Income: Optional[float] = None
    Travel_Time_Minutes: Optional[float] = None
    Semester_GPA: Optional[float] = None
    CGPA: Optional[float] = None


class StudentDetailResponse(BaseModel):
    id: str
    name: str
    studentId: str
    source: Literal["batch", "chat"]
    reviewed: bool
    assessed_at: str
    assessment: RiskAssessmentSchema
    features: Optional[AcademicFeatures] = None
