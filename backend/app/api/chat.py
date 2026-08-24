from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["chat"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # Mocked response until OpenAI/RAG is wired in
    return ChatResponse(
        reply=f"(mocked) I received your message: '{request.message}'. "
        "Real coverage analysis is not implemented yet."
    )
