import logging
import uuid
from datetime import datetime, timezone

from app.db.client import get_db
from app.services import risk_service

logger = logging.getLogger(__name__)


async def process_form(
    fields: dict,
    prediction_type: str,
    data_source: str,
    name: str | None = None,
    student_id: str | None = None,
) -> dict:
    """
    Structured-form handler. The client submits all required fields directly
    (no chat/LLM extraction), we run the risk assessment synchronously and
    persist the result so it surfaces in overview / sessions / students.

    Returns {"conversationId": ..., "data": RiskAssessment}.
    Raises ValueError if the selection is invalid or required fields are missing.
    """
    risk_service.validate_selection(data_source, prediction_type)
    required = risk_service.required_fields(data_source, prediction_type)
    missing = [f for f in required if fields.get(f) in (None, "")]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    # Only keep the fields the assessor expects, in case extras were sent.
    clean_fields = {f: fields[f] for f in required}

    assessment = risk_service.assess(clean_fields, prediction_type, data_source)

    conversation_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "_id": conversation_id,
        "source": "form",
        "dataSource": data_source,
        "predictionType": prediction_type,
        "turns": [],
        "fields": clean_fields,
        "assessment": assessment,
        "assessed_at": now,
        "created_at": now,
    }
    if name:
        doc["studentName"] = name
    if student_id:
        doc["studentId"] = student_id

    db = get_db()
    await db.conversations.insert_one(doc)

    logger.debug(
        "📝 [FORM] type=%s risk=%s prob=%.4f id=%s",
        prediction_type, assessment["riskLevel"], assessment["riskProb"], conversation_id,
    )

    return {"conversationId": conversation_id, "data": assessment}
