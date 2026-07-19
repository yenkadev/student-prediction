from pydantic import BaseModel
from typing import Literal, Union
from .batch import RiskAssessmentSchema


class ChatRequest(BaseModel):
    message: str
    conversationId: str | None = None
    predictionType: Literal["ml", "rule_based"]


class ChatNeedMoreInfoResponse(BaseModel):
    type: Literal["need_more_info"] = "need_more_info"
    conversationId: str
    question: str


class ChatResultResponse(BaseModel):
    type: Literal["result"] = "result"
    conversationId: str
    data: RiskAssessmentSchema


ChatResponse = Union[ChatNeedMoreInfoResponse, ChatResultResponse]
