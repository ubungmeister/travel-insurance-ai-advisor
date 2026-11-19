from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Conversation
from app.repositories.policy_repository import list_policies_by_auth_user_id
from app.schemas.conversation import ConversationCreateResponse
from app.services.policy_service import summarize_policy


def create_conversation(
    db: Session, auth_user_id: UUID
) -> ConversationCreateResponse:
    policies = list_policies_by_auth_user_id(db, auth_user_id)
    if not policies:
        return ConversationCreateResponse(
            status="no_policies",
            conversation_id=None,
            selected_policy=None,
            policy_choices=[],
        )

    selected_policy = policies[0] if len(policies) == 1 else None
    conversation = Conversation(
        user_id=policies[0].user_id,
        selected_policy_id=selected_policy.id if selected_policy is not None else None,
    )
    db.add(conversation)
    db.flush()
    result = ConversationCreateResponse(
        status="ready" if selected_policy is not None else "selection_required",
        conversation_id=conversation.id,
        selected_policy=(
            summarize_policy(selected_policy) if selected_policy is not None else None
        ),
        policy_choices=(
            []
            if selected_policy is not None
            else [summarize_policy(policy) for policy in policies]
        ),
    )
    db.commit()
    return result
