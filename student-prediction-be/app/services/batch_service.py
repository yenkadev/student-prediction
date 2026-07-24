"""Read CSV/Excel and assess in batches, synchronously or asynchronously."""

import io
import math
import uuid
from datetime import datetime, timezone
from typing import Any

import pandas as pd

from app.db.client import get_db
from app.services import risk_service


def _to_native(value: Any) -> Any:
    """Convert a numpy/pandas scalar to a Python type and turn NaN into None."""
    native = value.item() if hasattr(value, "item") else value
    if isinstance(native, float) and math.isnan(native):
        return None
    return native


def parse_file(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Read CSV or Excel from the uploaded content."""
    lower_name = filename.lower()
    if lower_name.endswith((".xlsx", ".xls")):
        return pd.read_excel(io.BytesIO(file_bytes))
    return pd.read_csv(io.BytesIO(file_bytes))


def assess_dataframe(
    frame: pd.DataFrame, data_source: str, prediction_type: str
) -> list[dict[str, Any]]:
    """Assess every row and return a list of students in the API schema."""
    required = risk_service.required_fields(data_source, prediction_type)
    missing_columns = [column for column in required if column not in frame.columns]
    if missing_columns:
        preview = ", ".join(missing_columns[:6])
        remaining = len(missing_columns) - 6
        suffix = f" and {remaining} more" if remaining > 0 else ""
        raise ValueError(
            f"File does not match the structure of {data_source}. "
            f"Missing {len(missing_columns)} required columns: {preview}{suffix}."
        )
    if frame.empty:
        raise ValueError("The uploaded file has no data rows.")

    results: list[dict[str, Any]] = []
    for index, row in frame.iterrows():
        features = {column: _to_native(row[column]) for column in required}
        assessment = risk_service.assess(features, prediction_type, data_source)

        # Accept research files without name/studentId by generating a stable identifier.
        raw_student_id = row.get("studentId")
        if _to_native(raw_student_id) is None:
            raw_student_id = row.get("Student_ID")
        if _to_native(raw_student_id) is None:
            raw_student_id = row.get("row_id")
        if _to_native(raw_student_id) is None:
            raw_student_id = index + 1
        student_id = str(_to_native(raw_student_id))

        raw_name = _to_native(row.get("name"))
        name = str(raw_name) if raw_name is not None else f"Student {student_id}"
        results.append(
            {
                "id": str(uuid.uuid4()),
                "name": name,
                "studentId": student_id,
                "reviewed": False,
                "assessment": assessment,
                "assessed_at": datetime.now(timezone.utc).isoformat(),
                "features": features,
            }
        )
    return results


def assess_file(
    file_bytes: bytes, filename: str, data_source: str, prediction_type: str
) -> list[dict[str, Any]]:
    """Pure helper shared by the synchronous API and the background job."""
    frame = parse_file(file_bytes, filename)
    return assess_dataframe(frame, data_source, prediction_type)


async def create_job(
    prediction_type: str, data_source: str, filename: str
) -> str:
    """Create a background job in MongoDB and return its job id."""
    risk_service.validate_selection(data_source, prediction_type)
    db = get_db()
    job_id = str(uuid.uuid4())
    await db.batch_jobs.insert_one(
        {
            "_id": job_id,
            "status": "processing",
            "progress": 0,
            "predictionType": prediction_type,
            "dataSource": data_source,
            "filename": filename,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "results": [],
            "error": None,
        }
    )
    return job_id


async def process_job(
    job_id: str,
    file_bytes: bytes,
    filename: str,
    prediction_type: str,
    data_source: str,
) -> None:
    """Process the background job and save the results to MongoDB."""
    db = get_db()
    try:
        results = assess_file(file_bytes, filename, data_source, prediction_type)
        await db.batch_jobs.update_one(
            {"_id": job_id},
            {
                "$set": {
                    "status": "done",
                    "progress": 100,
                    "results": results,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                }
            },
        )
    except Exception as error:
        await db.batch_jobs.update_one(
            {"_id": job_id},
            {"$set": {"status": "failed", "error": str(error)}},
        )


async def get_job(job_id: str) -> dict | None:
    """Read a background job by its identifier."""
    return await get_db().batch_jobs.find_one({"_id": job_id})
