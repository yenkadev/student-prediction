import uuid
from datetime import datetime, timezone

from app.db.client import get_db
from app.services import gemini, risk_service

MAX_TURNS = 5


async def process_chat(
    message: str,
    conversation_id: str | None,
    prediction_type: str,
    data_source: str,
) -> dict:
    """
    Main chat handler. Returns a dict with 'type' key:
    - {"type": "need_more_info", "conversationId": ..., "question": ...}
    - {"type": "result", "conversationId": ..., "data": RiskAssessment}
    Raises ValueError if turn limit exceeded.
    """
    risk_service.validate_selection(data_source, prediction_type)
    db = get_db()

    # Load or create conversation
    if conversation_id:
        conv = await db.conversations.find_one({"_id": conversation_id})
        if not conv:
            raise ValueError(f"Conversation {conversation_id} not found")
        if conv.get("predictionType") != prediction_type or conv.get("dataSource") != data_source:
            raise ValueError("Không thể thay đổi nguồn dữ liệu hoặc giải pháp trong hội thoại đang có.")
    else:
        conversation_id = str(uuid.uuid4())
        conv = {
            "_id": conversation_id,
            "predictionType": prediction_type,
            "dataSource": data_source,
            "turns": [],
            "fields": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.conversations.insert_one(conv)

    # Append user message
    conv["turns"].append({"role": "user", "content": message})

    # Check turn limit
    user_turns = sum(1 for t in conv["turns"] if t["role"] == "user")
    if user_turns > MAX_TURNS:
        raise ValueError("Maximum conversation turns exceeded. Please start a new assessment.")

    # Extract fields via Gemini
    required_fields = risk_service.required_fields(data_source, prediction_type)
    extracted = await gemini.extract_fields(conv["turns"], required_fields)

    # Merge into stored fields (only overwrite nulls with real values)
    for field, value in extracted.items():
        if value is not None:
            conv["fields"][field] = value

    # Save updated conversation
    await db.conversations.update_one(
        {"_id": conversation_id},
        {"$set": {"turns": conv["turns"], "fields": conv["fields"]}}
    )

    # Check if all required fields are present
    missing = [f for f in required_fields if conv["fields"].get(f) is None]

    if not missing:
        # All fields present — run prediction
        assessment = risk_service.assess(conv["fields"], prediction_type, data_source)
        await db.conversations.update_one(
            {"_id": conversation_id},
            {"$set": {
                "assessment": assessment,
                "assessed_at": datetime.now(timezone.utc).isoformat(),
            }}
        )
        return {
            "type": "result",
            "conversationId": conversation_id,
            "data": assessment,
        }

    # Still missing fields — ask Gemini for follow-up question
    question = await gemini.generate_followup_question(conv["turns"], missing)

    # Append assistant message to conversation
    conv["turns"].append({"role": "assistant", "content": question})
    await db.conversations.update_one(
        {"_id": conversation_id},
        {"$set": {"turns": conv["turns"]}}
    )

    return {
        "type": "need_more_info",
        "conversationId": conversation_id,
        "question": question,
    }
