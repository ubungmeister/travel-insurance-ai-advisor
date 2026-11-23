from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.seed import seed_database
from app.db.session import get_db
from app.dependencies.authentication import CurrentUser, get_current_user
from app.main import app
from app.models import Conversation, Message, Policy, User
from app.services import chat_service


@pytest.fixture
def persisted_api(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'chat.db'}")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _record):
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    owner_auth_id, other_auth_id = uuid4(), uuid4()
    with Session(engine) as db:
        seed_database(db)
        owner = db.scalars(select(User)).one()
        owner.auth_user_id = owner_auth_id
        db.add(User(email="other@example.com", auth_user_id=other_auth_id))
        db.commit()
        owner_id = owner.id

    def override_db():
        with Session(engine) as db:
            yield db

    def authenticate(auth_id):
        # Identical email deliberately: authorization must use the verified UUID.
        app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_user_id=auth_id, email="demo@example.com"
        )

    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            yield client, authenticate, engine, owner_auth_id, other_auth_id, owner_id
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)
        engine.dispose()


def create_owned(api):
    client, authenticate, _, owner_auth_id, *_ = api
    authenticate(owner_auth_id)
    response = client.post("/api/v1/conversations")
    assert response.status_code == 201
    return response.json()["conversation_id"]


def send(client, **payload):
    return client.post("/api/v1/chat", json={"request_id": str(uuid4()), **payload})


def first_payload(api):
    _, authenticate, engine, owner, *_ = api
    authenticate(owner)
    with Session(engine) as db:
        return {"policy_id": db.scalar(select(Policy.id)), "message": "Hello"}


@pytest.mark.parametrize("concurrent", [False, True])
def test_first_send_replay_creates_one_conversation_and_turn(persisted_api, concurrent):
    payload = {**first_payload(persisted_api), "request_id": str(uuid4())}
    client, _, engine, *_ = persisted_api
    if concurrent:
        barrier = Barrier(2)

        def attempt(_):
            barrier.wait(timeout=5)
            return send(client, **payload)

        with ThreadPoolExecutor(2) as pool:
            first, replay = pool.map(attempt, range(2))
    else:
        first, replay = send(client, **payload), send(client, **payload)
    assert first.status_code == replay.status_code == 200
    assert first.json() == replay.json()
    with Session(engine) as db:
        assert db.scalars(select(Conversation.id)).all() == [first.json()["conversation_id"]]
        assert db.scalars(select(Message.id).order_by(Message.id)).all() == [
            row["id"] for row in first.json()["messages"]
        ]


def test_exact_payload_and_target_conflicts_and_distinct_turns(persisted_api):
    payload = {**first_payload(persisted_api), "request_id": str(uuid4())}
    client, *_ = persisted_api
    first = send(client, **payload)
    assert first.status_code == 200
    target = first.json()["conversation_id"]
    for changed in [
        {**payload, "message": "Hello "},
        {**payload, "policy_id": payload["policy_id"] + 1},
        {"request_id": payload["request_id"], "conversation_id": target, "message": "Hello"},
    ]:
        assert send(client, **changed).status_code == 409
    next_payload = {"conversation_id": target, "message": "Hello", "request_id": str(uuid4())}
    second = send(client, **next_payload)
    assert second.status_code == 200
    assert send(client, **next_payload).json() == second.json()
    assert second.json()["messages"][0]["id"] != first.json()["messages"][0]["id"]
    assert len(client.get(f"/api/v1/conversations/{target}").json()["messages"]) == 4


def test_first_send_failure_rolls_back_and_same_key_can_retry(persisted_api, monkeypatch):
    payload = {**first_payload(persisted_api), "request_id": str(uuid4())}
    client, _, engine, *_ = persisted_api

    def fail(_):
        raise RuntimeError("no reply")

    with monkeypatch.context() as patch:
        patch.setattr(chat_service, "generate_reply", fail)
        assert send(client, **payload).status_code == 500
    with Session(engine) as db:
        assert not db.scalars(select(Conversation)).all()
        assert not db.scalars(select(Message)).all()
    assert send(client, **payload).status_code == 200


def test_first_send_checks_policy_and_exactly_one_target(persisted_api):
    payload = first_payload(persisted_api)
    client, authenticate, _, _, other, _ = persisted_api
    assert send(client, **{**payload, "policy_id": 0}).status_code == 422
    assert send(client, **payload, conversation_id=1).status_code == 422
    assert send(client, message="Hello").status_code == 422
    assert send(client, **payload, request_id="not-uuid").status_code == 422
    authenticate(other)
    assert send(client, **payload).status_code == 404
    assert send(client, **{**payload, "policy_id": 9999}).status_code == 404
    assert client.get("/api/v1/conversations").json() == []


def test_request_key_is_scoped_to_owner_and_deleted_result_is_not_recreated(persisted_api):
    payload = {**first_payload(persisted_api), "request_id": str(uuid4())}
    client, authenticate, engine, owner, other, _ = persisted_api
    result = send(client, **payload)
    assert result.status_code == 200
    conversation_id = result.json()["conversation_id"]
    authenticate(other)
    assert send(client, **payload).json() == {"detail": "Policy not found"}
    authenticate(owner)
    with Session(engine) as db:
        db.delete(db.get(Conversation, conversation_id))
        db.commit()
    assert send(client, **payload).status_code == 404
    with Session(engine) as db:
        assert not db.scalars(select(Conversation)).all()
        assert not db.scalars(select(Message)).all()


def test_sends_persisted_mock_turns_and_reloads_in_order(persisted_api):
    conversation_id = create_owned(persisted_api)
    client, _, engine, *_ = persisted_api
    saved = []
    for text in ["First question", "Second question"]:
        response = send(client, **{
            "conversation_id": conversation_id, "message": text,
        })
        assert response.status_code == 200
        turn = response.json()
        assert turn["reply"].startswith("(mocked)")
        assert "Real coverage analysis is not implemented yet." in turn["reply"]
        assert [m["role"] for m in turn["messages"]] == ["USER", "ASSISTANT"]
        assert [m["content"] for m in turn["messages"]] == [text, turn["reply"]]
        saved.extend(turn["messages"])

    # A new request/DB session restores saved records, not in-memory UI state.
    response = client.get(f"/api/v1/conversations/{conversation_id}")
    assert response.status_code == 200
    detail = response.json()
    assert detail["conversation_id"] == conversation_id
    assert detail["selected_policy"]["policy_number"] == "POL-2026-000001"
    assert detail["messages"] == saved
    assert [m["id"] for m in saved] == sorted(m["id"] for m in saved)
    assert all(m["created_at"] for m in saved)
    with Session(engine) as db:
        assert len(db.scalars(select(Message)).all()) == 4
        assert len(db.scalars(select(Conversation)).all()) == 1


def test_history_lists_only_owned_conversations_latest_activity_first(persisted_api):
    first = create_owned(persisted_api)
    client, _, engine, _, _, owner_id = persisted_api
    second = client.post("/api/v1/conversations").json()["conversation_id"]
    with Session(engine) as db:
        db.get(Conversation, first).created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
        db.get(Conversation, second).created_at = datetime(2026, 2, 1, tzinfo=timezone.utc)
        other = db.scalars(select(User).where(User.id != owner_id)).one()
        db.add(Conversation(user_id=other.id))
        db.commit()
    response = client.get("/api/v1/conversations")
    assert response.status_code == 200
    assert [c["conversation_id"] for c in response.json()] == [second, first]
    assert response.json()[0]["selected_policy"]["policy_number"] == "POL-2026-000001"

    assert send(client, **{
        "conversation_id": first, "message": "Resume this older conversation",
    }).status_code == 200
    history = client.get("/api/v1/conversations").json()
    assert [c["conversation_id"] for c in history] == [first, second]
    assert history[0]["last_activity_at"] >= history[0]["created_at"]


def test_message_order_uses_ids_when_timestamps_are_equal(persisted_api):
    conversation_id = create_owned(persisted_api)
    client, _, engine, *_ = persisted_api
    with Session(engine) as db:
        for role, text in [("USER", "one"), ("ASSISTANT", "two"), ("USER", "three")]:
            db.add(Message(
                conversation_id=conversation_id, role=role, content=text,
                created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            ))
        db.commit()
    response = client.get(f"/api/v1/conversations/{conversation_id}")
    assert response.status_code == 200
    assert [m["content"] for m in response.json()["messages"]] == ["one", "two", "three"]


@pytest.mark.parametrize("caller", ["other", "unlinked"])
def test_foreign_and_missing_conversations_deny_reads_and_writes(persisted_api, caller):
    conversation_id = create_owned(persisted_api)
    client, authenticate, engine, _, other_auth_id, _ = persisted_api
    authenticate(other_auth_id if caller == "other" else uuid4())
    for target in [conversation_id, conversation_id + 9999]:
        for response in [
            client.get(f"/api/v1/conversations/{target}"),
            send(client, conversation_id=target, message="secret?"),
        ]:
            assert response.status_code == 404
            assert response.json() == {"detail": "Conversation not found"}
    assert client.get("/api/v1/conversations").json() == []
    with Session(engine) as db:
        assert db.scalars(select(Message)).all() == []


def test_unbound_legacy_conversation_cannot_receive_messages(persisted_api):
    client, authenticate, engine, owner_auth_id, _, owner_id = persisted_api
    authenticate(owner_auth_id)
    with Session(engine) as db:
        conversation = Conversation(user_id=owner_id)
        db.add(conversation)
        db.commit()
        conversation_id = conversation.id
    response = send(client, **{
        "conversation_id": conversation_id, "message": "Hello",
    })
    assert response.status_code == 409
    assert client.get(f"/api/v1/conversations/{conversation_id}").json()["messages"] == []


def test_generation_failure_rolls_back_both_messages(persisted_api, monkeypatch):
    conversation_id = create_owned(persisted_api)
    client, _, engine, *_ = persisted_api

    def fail(_message):
        raise RuntimeError("mock generation failed")

    monkeypatch.setattr(chat_service, "generate_reply", fail)
    response = send(client, **{
        "conversation_id": conversation_id, "message": "Do not save half a turn",
    })
    assert response.status_code == 500
    with Session(engine) as db:
        assert db.scalars(select(Message)).all() == []


@pytest.mark.parametrize("conversation_id", [None, 0, -1, True, "1", 1.5])
def test_chat_rejects_invalid_conversation_id(persisted_api, conversation_id):
    client, authenticate, engine, owner_auth_id, *_ = persisted_api
    authenticate(owner_auth_id)
    response = send(client, **{
        "conversation_id": conversation_id, "message": "Hello",
    })
    assert response.status_code == 422
    with Session(engine) as db:
        assert db.scalars(select(Message)).all() == []


def test_history_endpoints_require_authentication(persisted_api):
    client, *_ = persisted_api
    assert client.get("/api/v1/conversations").status_code == 401
    assert client.get("/api/v1/conversations/1").status_code == 401


def test_empty_history_does_not_create_conversation(persisted_api):
    client, authenticate, engine, owner_auth_id, *_ = persisted_api
    authenticate(owner_auth_id)
    response = client.get("/api/v1/conversations")
    assert response.status_code == 200
    assert response.json() == []
    with Session(engine) as db:
        assert db.scalars(select(Conversation)).all() == []


def test_turn_timestamps_are_taken_after_obtaining_the_lock(persisted_api, monkeypatch):
    conversation_id = create_owned(persisted_api)
    client, _, engine, *_ = persisted_api
    locked = False
    original = chat_service.get_owned_conversation
    after_lock = datetime(2031, 1, 1, 12, 0, 0, 123456, tzinfo=timezone.utc)

    def lock(*args, **kwargs):
        nonlocal locked
        result = original(*args, **kwargs)
        locked = True
        return result

    class Clock:
        @staticmethod
        def now(tz):
            assert locked
            return after_lock

    monkeypatch.setattr(chat_service, "get_owned_conversation", lock)
    monkeypatch.setattr(chat_service, "datetime", Clock, raising=False)
    response = send(client, **{
        "conversation_id": conversation_id, "message": "Waited for a lock",
    })
    assert response.status_code == 200
    with Session(engine) as db:
        messages = db.scalars(select(Message)).all()
        assert len(messages) == 2
        assert all(m.created_at.replace(tzinfo=timezone.utc) == after_lock for m in messages)
