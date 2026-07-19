import io
import uuid

import pandas as pd

from app.db.client import get_db
from app.services import risk_service

ML_REQUIRED = [
    "name", "studentId", "Gender", "Internet_Access", "Part_Time_Job",
    "Scholarship", "Semester", "Department", "Parental_Education",
    "Age", "Family_Income", "Study_Hours_per_Day", "Attendance_Rate",
    "Assignment_Delay_Days", "Travel_Time_Minutes", "Stress_Index",
    "GPA", "Semester_GPA", "CGPA"
]
RULE_BASED_REQUIRED = [
    "name", "studentId", "GPA", "Attendance_Rate", "Stress_Index",
    "Study_Hours_per_Day", "Assignment_Delay_Days", "Internet_Access", "Part_Time_Job"
]


async def create_job(prediction_type: str) -> str:
    """Create a new batch job document. Returns job_id."""
    db = get_db()
    job_id = str(uuid.uuid4())
    await db.batch_jobs.insert_one({
        "_id": job_id,
        "status": "processing",
        "progress": 0,
        "predictionType": prediction_type,
        "results": [],
        "error": None,
    })
    return job_id


async def process_job(job_id: str, file_bytes: bytes, filename: str, prediction_type: str) -> None:
    """
    Background task: parse CSV/Excel, run risk assessment per row, update job in MongoDB.
    """
    db = get_db()

    try:
        # Parse file
        if filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(file_bytes))
        else:
            df = pd.read_csv(io.BytesIO(file_bytes))

        # Validate required columns
        required = ML_REQUIRED if prediction_type == "ml" else RULE_BASED_REQUIRED
        missing_cols = [c for c in required if c not in df.columns]
        if missing_cols:
            await db.batch_jobs.update_one(
                {"_id": job_id},
                {"$set": {"status": "failed", "error": f"Missing columns: {missing_cols}"}}
            )
            return

        total = len(df)
        results = []

        for i, row in df.iterrows():
            feature_cols = [c for c in required if c not in ("name", "studentId")]
            fields = {col: row[col] for col in feature_cols}
            assessment = risk_service.assess(fields, prediction_type)
            results.append({
                "id": str(uuid.uuid4()),
                "name": str(row["name"]),
                "studentId": str(row["studentId"]),
                "reviewed": False,
                "assessment": assessment,
            })
            progress = int((i + 1) / total * 100)  # type: ignore[operator]
            await db.batch_jobs.update_one(
                {"_id": job_id},
                {"$set": {"progress": progress}}
            )

        await db.batch_jobs.update_one(
            {"_id": job_id},
            {"$set": {"status": "done", "progress": 100, "results": results}}
        )

    except Exception as e:
        await db.batch_jobs.update_one(
            {"_id": job_id},
            {"$set": {"status": "failed", "error": str(e)}}
        )


async def get_job(job_id: str) -> dict | None:
    """Fetch job document by id."""
    db = get_db()
    return await db.batch_jobs.find_one({"_id": job_id})
