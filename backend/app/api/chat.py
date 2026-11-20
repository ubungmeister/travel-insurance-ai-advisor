from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.authentication import CurrentUser, get_current_user
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import send_message

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return send_message(db, current_user.auth_user_id, request)
