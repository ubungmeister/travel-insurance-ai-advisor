from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    Conversation, InsurancePlanVersion, Message, PlanVariant, Policy, User,
)


def _owned_conversations(auth_user_id: UUID):
    return (
        select(Conversation)
        .join(User, Conversation.user_id == User.id)
        .where(User.auth_user_id == auth_user_id)
        .options(
            selectinload(Conversation.selected_policy)
            .selectinload(Policy.plan_variant)
            .selectinload(PlanVariant.plan_version)
            .selectinload(InsurancePlanVersion.plan)
        )
    )


def get_owned_conversation(
    db: Session, auth_user_id: UUID, conversation_id: int, *, for_update: bool = False
) -> Conversation:
    """Find a conversation without revealing whether another user owns its ID.

    Missing and foreign IDs get the same 404. Use the optional lock only for
    writes that serialize turns; detail reads and replays do not need it.
    """
    statement = _owned_conversations(auth_user_id).where(
        Conversation.id == conversation_id
    )
    if for_update:
        statement = statement.with_for_update(of=Conversation)
    conversation = db.scalar(statement)
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )
    return conversation


def list_owned_conversations(db: Session, auth_user_id: UUID):
    """Order owned chats by last message time, including chats with no messages.

    Empty chats use creation time. The descending ID tie-breaker keeps the
    home route's most-recent selection deterministic at equal timestamps.
    """
    activity = (
        select(
            Message.conversation_id, func.max(Message.created_at).label("last_message_at")
        )
        .group_by(Message.conversation_id)
        .subquery()
    )
    last_activity = func.coalesce(activity.c.last_message_at, Conversation.created_at)
    statement = (
        _owned_conversations(auth_user_id)
        .outerjoin(activity, activity.c.conversation_id == Conversation.id)
        .add_columns(last_activity.label("last_activity_at"))
        .order_by(last_activity.desc(), Conversation.id.desc())
    )
    return db.execute(statement).all()
