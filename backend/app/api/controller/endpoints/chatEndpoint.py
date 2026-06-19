from fastapi import APIRouter, HTTPException
from app.schemas.chatSchema import ChatMessageRequest, ChatMessageResponse
from app.services.chatService import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])
chatService = ChatService()


@router.post("/", response_model=ChatMessageResponse)
async def sendMessage(body: ChatMessageRequest):
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="Tin nhắn không được để trống")
    result = await chatService.processMessage(body.message, body.conversationHistory or [])
    return result
