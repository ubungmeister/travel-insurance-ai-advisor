from fastapi import APIRouter, Depends

from app.dependencies.authentication import get_current_user
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import generate_reply

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    dependencies=[Depends(get_current_user)],
)
def chat(request: ChatRequest):
    reply = generate_reply(request.message)
    return ChatResponse(reply=reply)
