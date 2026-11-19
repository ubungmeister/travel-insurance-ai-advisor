from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Conversation
from app.repositories.policy_repository import list_policies_by_auth_user_id
from app.schemas.conversation import ConversationCreateResponse
from app.services.policy_service import summarize_policy


def create_conversation(
    db: Session, auth_user_id: UUID, policy_id: int | None = None
) -> ConversationCreateResponse:
    policies = list_policies_by_auth_user_id(db, auth_user_id)
    selected_policy = None
    if policy_id is not None:
        selected_policy = next((p for p in policies if p.id == policy_id), None)
        if selected_policy is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found"
            )

    if not policies:
        return ConversationCreateResponse(
            status="no_policies",
            conversation_id=None,
            selected_policy=None,
            policy_choices=[],
        )

    if selected_policy is None and len(policies) == 1:
        selected_policy = policies[0]
    if selected_policy is None:
        return ConversationCreateResponse(
            status="selection_required",
            conversation_id=None,
            selected_policy=None,
            policy_choices=[summarize_policy(policy) for policy in policies],
        )

    conversation = Conversation(
        user_id=selected_policy.user_id,
        selected_policy_id=selected_policy.id,
    )
    db.add(conversation)
    db.flush()
    result = ConversationCreateResponse(
        status="ready",
        conversation_id=conversation.id,
        selected_policy=summarize_policy(selected_policy),
        policy_choices=[],
    )
    db.commit()
    return result
