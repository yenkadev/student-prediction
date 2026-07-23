import logging
import math
from app.db.client import get_db

logger = logging.getLogger(__name__)


def _clean_nan(val):
    """Recursively replace NaN floats with None so every value is JSON-safe."""
    if isinstance(val, float) and math.isnan(val):
        return None
    if isinstance(val, dict):
        return {k: _clean_nan(v) for k, v in val.items()}
    if isinstance(val, list):
        return [_clean_nan(item) for item in val]
    return val


async def get_student(student_id: str) -> dict | None:
    db = get_db()

    # --- Try batch_jobs first ---
    pipeline = [
        {"$match": {"results.id": student_id}},
        {"$unwind": "$results"},
        {"$match": {"results.id": student_id}},
        {"$replaceRoot": {"newRoot": "$results"}},
        {"$addFields": {"source": "batch"}},
        {"$limit": 1},
    ]
    batch_hits = await db.batch_jobs.aggregate(pipeline).to_list(length=1)
    if batch_hits:
        doc = batch_hits[0]
        logger.debug("[STUDENT] found in batch_jobs id=%s", student_id)
        return _clean_nan(doc)

    # --- Fallback: completed chat conversation ---
    conv = await db.conversations.find_one(
        {"_id": student_id, "assessment": {"$exists": True}}
    )
    if conv:
        logger.debug("[STUDENT] found in conversations id=%s", student_id)
        source = conv.get("source", "chat")
        default_name = "Form Assessment" if source == "form" else "Chat Assessment"
        result = {
            "id": conv["_id"],
            "name": conv.get("studentName", default_name),
            "studentId": conv.get("studentId", conv["_id"]),
            "reviewed": False,
            "assessed_at": conv.get("assessed_at", ""),
            "assessment": conv["assessment"],
            "features": conv.get("fields") or None,
            "source": source,
        }
        return _clean_nan(result)

    logger.debug("[STUDENT] not found id=%s", student_id)
    return None
