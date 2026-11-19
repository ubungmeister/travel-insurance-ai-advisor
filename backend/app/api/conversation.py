from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.authentication import CurrentUser, get_current_user
from app.schemas.conversation import ConversationCreateRequest, ConversationCreateResponse
from app.services.conversation_service import create_conversation


router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


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
