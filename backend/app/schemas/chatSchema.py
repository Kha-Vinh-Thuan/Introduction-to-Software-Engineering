from pydantic import BaseModel
from typing import Optional


class ChatMessageRequest(BaseModel):
    message: str
    conversationHistory: Optional[list[dict]] = []


class ChatMessageResponse(BaseModel):
    reply: str
    toolCalls: Optional[list[dict]] = []
    sqlExecuted: Optional[str] = None
