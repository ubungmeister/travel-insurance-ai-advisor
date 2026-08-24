from fastapi import APIRouter
from pydantic import BaseModel

from app.services.chat_service import generate_reply

router = APIRouter(prefix="/api/v1", tags=["chat"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    reply = generate_reply(request.message)
    return ChatResponse(reply=reply)
