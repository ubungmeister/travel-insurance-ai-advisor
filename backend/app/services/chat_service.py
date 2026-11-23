from datetime import datetime, timezone
from hashlib import sha256
import json
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from app.models import ChatReceipt, Conversation, Message, MessageRole, Policy, User
from app.repositories.conversation_repository import get_owned_conversation
from app.schemas.chat import ChatRequest, ChatResponse, MessageResponse


def generate_reply(message: str) -> str:
    return (
        f"(mocked) I received your message: '{message}'. "
        "Real coverage analysis is not implemented yet."
    )


def _saved_turn(conversation_id: int, user: Message, assistant: Message) -> ChatResponse:
    return ChatResponse(
        conversation_id=conversation_id,
        reply=assistant.content,
        messages=[MessageResponse.model_validate(row) for row in (user, assistant)],
    )


def send_message(db: Session, auth_user_id: UUID, request: ChatRequest) -> ChatResponse:
    """Persist or replay one mock turn for the authenticated account.

    The receipt keys the exact submitted target and text, even though saved
    messages are trimmed. Claim it in the same transaction as the conversation
    (if new) and both messages, so a failed write leaves nothing to replay and
    concurrent requests with the same key cannot commit twice. An existing
    receipt returns the original turn, never a new one for a deleted result.

    The existing-conversation lock serializes turns. Only the fast local mock
    belongs inside that transaction; future remote inference must run outside it.
    """
    user_id = db.scalar(select(User.id).where(User.auth_user_id == auth_user_id))
    missing = "Policy not found" if request.policy_id is not None else "Conversation not found"
    if user_id is None:
        raise HTTPException(status_code=404, detail=missing)

    fingerprint = sha256(json.dumps(
        [request.conversation_id, request.policy_id, request.message], ensure_ascii=True,
    ).encode()).hexdigest()
    insert = sqlite_insert if db.get_bind().dialect.name == "sqlite" else pg_insert
    message = request.message.strip()
    try:
        # A concurrent duplicate waits for this transaction to commit or roll back.
        claimed = db.scalar(
            insert(ChatReceipt)
            .values(user_id=user_id, request_id=request.request_id, fingerprint=fingerprint)
            .on_conflict_do_nothing(index_elements=[ChatReceipt.user_id, ChatReceipt.request_id])
            .returning(ChatReceipt.request_id)
        )
        receipt = db.get(ChatReceipt, (user_id, request.request_id))
        assert receipt is not None
        if claimed is None:
            if receipt.fingerprint != fingerprint:
                raise HTTPException(status_code=409, detail="Request ID already used with a different payload")
            if receipt.conversation_id is not None:
                get_owned_conversation(db, auth_user_id, receipt.conversation_id)
                user = db.get(Message, receipt.user_message_id) if receipt.user_message_id is not None else None
                assistant = db.get(Message, receipt.assistant_message_id) if receipt.assistant_message_id is not None else None
                if user is not None and assistant is not None:
                    result = _saved_turn(receipt.conversation_id, user, assistant)
                    db.commit()
                    return result
            raise HTTPException(status_code=404, detail="Saved turn is unavailable")

        if request.policy_id is not None:
            policy_id = db.scalar(select(Policy.id).where(
                Policy.id == request.policy_id, Policy.user_id == user_id,
            ))
            if policy_id is None:
                raise HTTPException(status_code=404, detail=missing)
            conversation = Conversation(user_id=user_id, selected_policy_id=policy_id)
            db.add(conversation)
            db.flush()
        else:
            assert request.conversation_id is not None
            conversation = get_owned_conversation(
                db, auth_user_id, request.conversation_id, for_update=True,
            )
            if conversation.selected_policy_id is None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Conversation has no selected policy; start a new chat",
                )
        user_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=message,
            created_at=datetime.now(timezone.utc),
        )
        db.add(user_message)
        db.flush()
        reply = generate_reply(message)
        assistant_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=reply,
            created_at=datetime.now(timezone.utc),
        )
        db.add(assistant_message)
        db.flush()
        receipt.conversation_id = conversation.id
        receipt.user_message_id = user_message.id
        receipt.assistant_message_id = assistant_message.id
        result = _saved_turn(conversation.id, user_message, assistant_message)
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise
