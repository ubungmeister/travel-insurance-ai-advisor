from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

from app.services.chat_service import generate_reply

router = APIRouter(prefix="/api/v1", tags=["chat"])

MAX_MESSAGE_LENGTH = 2000


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    message: str = Field(min_length=1, max_length=MAX_MESSAGE_LENGTH)


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    reply = generate_reply(request.message)
    return ChatResponse(reply=reply)
