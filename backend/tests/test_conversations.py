from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.seed import seed_database
from app.db.session import get_db
from app.dependencies.authentication import CurrentUser, get_current_user
from app.main import app
from app.models import Conversation, Message, Policy, User


URL = "/api/v1/conversations"


@pytest.fixture
def conversation_api():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _record):
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    owner_auth_id, empty_auth_id = uuid4(), uuid4()
    with Session(engine) as db:
        seed_database(db)
        owner = db.scalars(select(User)).one()
        owner.auth_user_id = owner_auth_id
        db.add(User(email="empty@example.com", auth_user_id=empty_auth_id))
        db.commit()
        owner_id = owner.id

    def override_db():
        with Session(engine) as db:
            yield db

    def authenticate(auth_id):
        app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_user_id=auth_id, email="demo@example.com"
        )

    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app) as client:
            yield client, authenticate, engine, owner_auth_id, empty_auth_id, owner_id
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)
        engine.dispose()


def test_creation_requires_authentication(conversation_api):
    client, _, engine, *_ = conversation_api
    response = client.post(URL)
    assert response.status_code == 401
    with Session(engine) as db:
        assert db.scalars(select(Conversation)).all() == []


@pytest.mark.parametrize("linked_user", [True, False], ids=["no-policies", "no-local-user"])
def test_no_policies_does_not_create_conversation(conversation_api, linked_user):
    client, authenticate, engine, _, empty_auth_id, _ = conversation_api
    authenticate(empty_auth_id if linked_user else uuid4())

    response = client.post(URL)

    assert response.status_code == 200
    assert response.json() == {
        "status": "no_policies",
        "conversation_id": None,
        "selected_policy": None,
        "policy_choices": [],
    }
    with Session(engine) as db:
        assert db.scalars(select(Conversation)).all() == []


def test_one_policy_is_selected_and_conversation_is_persisted(conversation_api):
    client, authenticate, engine, owner_auth_id, _, owner_id = conversation_api
    authenticate(owner_auth_id)

    response = client.post(URL)

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "ready"
    assert body["policy_choices"] == []
    assert body["selected_policy"]["policy_number"] == "POL-2026-000001"
    assert body["selected_policy"]["plan_name"] == "Dominant"
    with Session(engine) as db:
        conversation = db.get(Conversation, body["conversation_id"])
        assert conversation is not None
        assert conversation.user_id == owner_id
        assert conversation.selected_policy_id == body["selected_policy"]["policy_id"]
        assert db.scalars(select(Message)).all() == []


def test_multiple_policies_return_only_owners_choices_without_selection(conversation_api):
    client, authenticate, engine, owner_auth_id, _, owner_id = conversation_api
    with Session(engine) as db:
        original = db.scalars(select(Policy)).one()
        other = User(email="other@example.com", auth_user_id=uuid4())
        db.add(other)
        db.flush()
        for user_id, number in [(owner_id, "OWNER-SECOND"), (other.id, "OTHER-POLICY")]:
            db.add(
                Policy(
                    user_id=user_id,
                    policy_number=number,
                    plan_variant_id=original.plan_variant_id,
                    terms_version_id=original.terms_version_id,
                    trip_purpose=original.trip_purpose,
                    declared_sport_category=original.declared_sport_category,
                    start_date=original.start_date,
                    end_date=original.end_date,
                    status="ISSUED",
                    price_paid=original.price_paid,
                    currency=original.currency,
                )
            )
        db.commit()
    authenticate(owner_auth_id)

    response = client.post(URL)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "selection_required"
    assert body["conversation_id"] is None
    assert body["selected_policy"] is None
    assert {item["policy_number"] for item in body["policy_choices"]} == {
        "POL-2026-000001", "OWNER-SECOND"
    }
    assert all(
        {"policy_id", "policy_number", "plan_name", "territory", "start_date", "end_date"}
        <= item.keys()
        for item in body["policy_choices"]
    )
    with Session(engine) as db:
        assert db.scalars(select(Conversation)).all() == []

    chosen = next(p for p in body["policy_choices"] if p["policy_number"] == "OWNER-SECOND")
    response = client.post(URL, json={"policy_id": chosen["policy_id"]})
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "ready"
    assert body["selected_policy"] == chosen
    assert body["policy_choices"] == []
    with Session(engine) as db:
        conversation = db.scalars(select(Conversation)).one()
        assert conversation.id == body["conversation_id"]
        assert conversation.user_id == owner_id
        assert conversation.selected_policy_id == chosen["policy_id"]
        assert db.scalars(select(Message)).all() == []


@pytest.mark.parametrize("caller", ["owner", "empty", "unlinked"])
def test_unavailable_policy_returns_404_without_creating_conversation(conversation_api, caller):
    client, authenticate, engine, owner_auth_id, empty_auth_id, _ = conversation_api
    authenticate({"owner": owner_auth_id, "empty": empty_auth_id, "unlinked": uuid4()}[caller])
    with Session(engine) as db:
        policy_id = db.scalars(select(Policy.id)).one()

    ids = [policy_id + 9999]
    if caller != "owner":
        ids.append(policy_id)
    for selected_id in ids:
        response = client.post(URL, json={"policy_id": selected_id})
        assert response.status_code == 404
        assert response.json() == {"detail": "Policy not found"}
    with Session(engine) as db:
        assert db.scalars(select(Conversation)).all() == []


def test_single_policy_owner_cannot_select_another_users_policy(conversation_api):
    client, authenticate, engine, owner_auth_id, _, _ = conversation_api
    with Session(engine) as db:
        original = db.scalars(select(Policy)).one()
        other = User(email="other@example.com", auth_user_id=uuid4())
        db.add(other)
        db.flush()
        foreign = Policy(
            user_id=other.id, policy_number="FOREIGN",
            plan_variant_id=original.plan_variant_id, terms_version_id=original.terms_version_id,
            trip_purpose=original.trip_purpose, declared_sport_category=original.declared_sport_category,
            start_date=original.start_date, end_date=original.end_date, status=original.status,
            price_paid=original.price_paid, currency=original.currency,
        )
        db.add(foreign)
        db.commit()
        foreign_id = foreign.id
    authenticate(owner_auth_id)
    response = client.post(URL, json={"policy_id": foreign_id})
    assert response.status_code == 404
    assert response.json() == {"detail": "Policy not found"}
    with Session(engine) as db:
        assert db.scalars(select(Conversation)).all() == []


@pytest.mark.parametrize("body", [
    {"policy_id": 0}, {"policy_id": -1}, {"policy_id": "1"},
    {"policy_id": True}, {"policy_id": 1.5}, {"policy_id": []},
    {"user_id": 1}, {"policy_id": 1, "auth_user_id": str(uuid4())},
])
def test_creation_rejects_invalid_selection_and_identity_fields(conversation_api, body):
    client, authenticate, engine, owner_auth_id, _, _ = conversation_api
    authenticate(owner_auth_id)
    response = client.post(URL, json=body)
    assert response.status_code == 422
    with Session(engine) as db:
        assert db.scalars(select(Conversation)).all() == []


def test_explicit_policy_selection_requires_authentication(conversation_api):
    client, _, engine, *_ = conversation_api
    response = client.post(URL, json={"policy_id": 1})
    assert response.status_code == 401
    with Session(engine) as db:
        assert db.scalars(select(Conversation)).all() == []


@pytest.mark.parametrize("body", [{}, {"policy_id": None}])
def test_empty_selection_auto_selects_single_policy(conversation_api, body):
    client, authenticate, engine, owner_auth_id, _, _ = conversation_api
    authenticate(owner_auth_id)
    response = client.post(URL, json=body)
    assert response.status_code == 201
    result = response.json()
    assert result["status"] == "ready"
    with Session(engine) as db:
        conversation = db.scalars(select(Conversation)).one()
        assert conversation.selected_policy_id == result["selected_policy"]["policy_id"]
