from typing import Annotated

from fastapi import APIRouter, Depends, Path, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.authentication import CurrentUser, get_current_user
from app.schemas.conversation import (
    ConversationCreateRequest, ConversationCreateResponse, ConversationDetail, ConversationSummary,
)
from app.services.conversation_service import create_conversation, get_conversation, list_conversations


router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


@router.get("", response_model=list[ConversationSummary])
def get_conversations(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ConversationSummary]:
    return list_conversations(db, current_user.auth_user_id)


@router.get("/{conversation_id}", response_model=ConversationDetail)
def get_conversation_detail(
    conversation_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConversationDetail:
    return get_conversation(db, current_user.auth_user_id, conversation_id)


@router.post(
    "",
    response_model=ConversationCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_200_OK: {"model": ConversationCreateResponse}},
)
def post_conversation(
    response: Response,
    request: ConversationCreateRequest | None = None,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConversationCreateResponse:
    result = create_conversation(
        db, current_user.auth_user_id, request.policy_id if request else None
    )
    if result.status != "ready":
        response.status_code = status.HTTP_200_OK
    return result
