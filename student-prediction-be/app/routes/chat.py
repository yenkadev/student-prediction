from fastapi import APIRouter, HTTPException, Response
from app.schemas.chat import ChatRequest
from app.db.client import get_db
from app.services import chat_service

router = APIRouter()


@router.post("/predict/chat", response_model=None)
async def predict_chat(request: ChatRequest) -> dict:
    try:
        result = await chat_service.process_chat(
            message=request.message,
            conversation_id=request.conversationId,
            prediction_type=request.predictionType,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(conversation_id: str) -> Response:
    db = get_db()
    result = await db.conversations.delete_one({"_id": conversation_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Conversation {conversation_id!r} not found")
    return Response(status_code=204)


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str) -> dict:
    db = get_db()
    conv = await db.conversations.find_one({"_id": conversation_id})
    if not conv:
        raise HTTPException(status_code=404, detail=f"Conversation {conversation_id!r} not found")
    return {
        "id": conv["_id"],
        "turns": conv.get("turns", []),
        "fields": conv.get("fields", {}),
        "assessment": conv.get("assessment"),
        "assessed_at": conv.get("assessed_at"),
        "created_at": conv.get("created_at", ""),
    }
