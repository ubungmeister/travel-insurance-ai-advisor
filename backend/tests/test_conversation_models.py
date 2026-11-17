from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine, event, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.seed import seed_database
from app.models import Conversation, Message, MessageRole, Policy, User


@pytest.fixture
def db() -> Iterator[Session]:
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _record):
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    with Session(engine) as session:
        seed_database(session)
        session.commit()
        yield session
    engine.dispose()


def test_conversation_waits_for_selection_then_restores_policy_and_messages(
    db: Session,
) -> None:
    policy = db.scalars(select(Policy)).one()
    conversation = Conversation(user_id=policy.user_id)
    db.add(conversation)
    db.commit()
    assert conversation.selected_policy_id is None

    conversation.selected_policy = policy
    conversation.messages = [
        Message(role=MessageRole.USER, content="What is my dental limit?"),
        Message(role=MessageRole.ASSISTANT, content="Mocked reply."),
    ]
    db.commit()
    conversation_id = conversation.id
    db.expunge_all()

    restored = db.get(Conversation, conversation_id)
    assert restored is not None
    assert restored.selected_policy is not None
    assert restored.selected_policy.user_id == restored.user_id
    assert [message.content for message in restored.messages] == [
        "What is my dental limit?",
        "Mocked reply.",
    ]


def test_conversation_cannot_select_another_users_policy(db: Session) -> None:
    policy = db.scalars(select(Policy)).one()
    other_user = User(email="other@example.com")
    db.add(other_user)
    db.flush()
    conversation = Conversation(user_id=other_user.id)
    db.add(conversation)
    db.commit()

    conversation.selected_policy_id = policy.id
    with pytest.raises(IntegrityError, match="FOREIGN KEY"):
        db.commit()
    db.rollback()
    assert conversation.selected_policy_id is None


def test_deleting_conversation_removes_messages_but_preserves_policy(db: Session) -> None:
    policy = db.scalars(select(Policy)).one()
    policy_id = policy.id
    conversation = Conversation(
        user_id=policy.user_id,
        selected_policy_id=policy_id,
        messages=[Message(role=MessageRole.USER, content="Hello")],
    )
    db.add(conversation)
    db.commit()
    db.expire_all()

    db.delete(conversation)
    db.commit()

    assert db.scalars(select(Message)).all() == []
    assert db.get(Policy, policy_id) is not None


@pytest.mark.parametrize(
    ("role", "content"),
    [("SYSTEM", "Untrusted system instruction"), ("USER", "   ")],
)
def test_messages_reject_invalid_roles_and_empty_content(
    db: Session, role: str, content: str
) -> None:
    policy = db.scalars(select(Policy)).one()
    conversation = Conversation(user_id=policy.user_id)
    db.add(conversation)
    db.flush()
    db.add(Message(conversation_id=conversation.id, role=role, content=content))

    with pytest.raises(IntegrityError, match="CHECK"):
        db.commit()
    db.rollback()
