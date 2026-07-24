"""Đọc CSV/Excel và đánh giá đồng bộ hoặc bất đồng bộ theo lô."""

import io
import math
import uuid
from datetime import datetime, timezone
from typing import Any

import pandas as pd

from app.db.client import get_db
from app.services import risk_service


def _to_native(value: Any) -> Any:
    """Chuyển scalar của numpy/pandas sang kiểu Python và đổi NaN thành None."""
    native = value.item() if hasattr(value, "item") else value
    if isinstance(native, float) and math.isnan(native):
        return None
    return native


def parse_file(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Đọc CSV hoặc Excel từ nội dung upload."""
    lower_name = filename.lower()
    if lower_name.endswith((".xlsx", ".xls")):
        return pd.read_excel(io.BytesIO(file_bytes))
    return pd.read_csv(io.BytesIO(file_bytes))


def assess_dataframe(
    frame: pd.DataFrame, data_source: str, prediction_type: str
) -> list[dict[str, Any]]:
    """Đánh giá mọi dòng và trả về danh sách sinh viên theo schema API."""
    required = risk_service.required_fields(data_source, prediction_type)
    missing_columns = [column for column in required if column not in frame.columns]
    if missing_columns:
        preview = ", ".join(missing_columns[:6])
        remaining = len(missing_columns) - 6
        suffix = f" và {remaining} cột khác" if remaining > 0 else ""
        raise ValueError(
            f"File không đúng cấu trúc của {data_source}. "
            f"Thiếu {len(missing_columns)} cột bắt buộc: {preview}{suffix}."
        )
    if frame.empty:
        raise ValueError("File upload không có dòng dữ liệu.")

    results: list[dict[str, Any]] = []
    for index, row in frame.iterrows():
        features = {column: _to_native(row[column]) for column in required}
        assessment = risk_service.assess(features, prediction_type, data_source)

        # Chấp nhận file nghiên cứu không có name/studentId bằng cách tạo định danh ổn định.
        raw_student_id = row.get("studentId")
        if _to_native(raw_student_id) is None:
            raw_student_id = row.get("Student_ID")
        if _to_native(raw_student_id) is None:
            raw_student_id = row.get("row_id")
        if _to_native(raw_student_id) is None:
            raw_student_id = index + 1
        student_id = str(_to_native(raw_student_id))

        raw_name = _to_native(row.get("name"))
        name = str(raw_name) if raw_name is not None else f"Sinh viên {student_id}"
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
    """Hàm thuần dùng chung cho API đồng bộ và background job."""
    frame = parse_file(file_bytes, filename)
    return assess_dataframe(frame, data_source, prediction_type)


async def create_job(
    prediction_type: str, data_source: str, filename: str
) -> str:
    """Tạo background job trong MongoDB và trả về mã job."""
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
    """Xử lý background job và lưu kết quả vào MongoDB."""
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
    """Đọc background job theo mã định danh."""
    return await get_db().batch_jobs.find_one({"_id": job_id})
