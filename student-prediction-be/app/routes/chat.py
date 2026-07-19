from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest
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
