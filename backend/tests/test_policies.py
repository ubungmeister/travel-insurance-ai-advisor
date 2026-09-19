from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.seed import seed_database
from app.db.session import get_db
from app.dependencies.authentication import CurrentUser, get_current_user
from app.main import app
from app.models import Policy, User

POLICIES_URL = "/api/v1/policies"


@pytest.fixture
def policy_api():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    owner_id, other_id, empty_id = uuid4(), uuid4(), uuid4()

    with Session(engine) as db:
        seed_database(db)
        owner = db.scalar(select(User).where(User.email == "demo@example.com"))
        owner.auth_user_id = owner_id
        other = User(email="other@example.com", auth_user_id=other_id)
        db.add_all([other, User(email="empty@example.com", auth_user_id=empty_id)])

        original = db.scalar(select(Policy))
        original.status = "EXPIRED"

        for user, number, start in [
            (owner, "OWNER-FUTURE", date(2030, 1, 1)),
            (other, "OTHER-POLICY", date(2031, 1, 1)),
        ]:
            db.add(
                Policy(
                    user=user,
                    plan_variant_id=original.plan_variant_id,
                    policy_number=number,
                    trip_purpose=original.trip_purpose,
                    declared_sport_category=original.declared_sport_category,
                    start_date=start,
                    end_date=start,
                    status="ACTIVE",
                    price_paid=Decimal("45.00"),
                    currency=original.currency,
                )
            )
        db.commit()

    def override_db():
        with Session(engine) as db:
            yield db

    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_db

    def authenticate(auth_id: object) -> None:
        # Deliberately identical email: only the verified UUID should select data.
        app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_user_id=auth_id, email="demo@example.com"
        )

    try:
        with TestClient(app) as client:
            yield client, authenticate, owner_id, other_id, empty_id
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)
        engine.dispose()


def test_requires_auth():
    response = TestClient(app).get(POLICIES_URL)
    assert response.status_code == 401


def test_lists_only_owners_policies_including_past_and_future(policy_api):
    client, authenticate, owner_id, _, _ = policy_api
    authenticate(owner_id)

    response = client.get(POLICIES_URL)

    assert response.status_code == 200
    items = response.json()
    assert len(items) == 2
    assert items[0]["policy_number"] == "OWNER-FUTURE"
    assert items[0]["status"] == "ACTIVE"
    assert items[0]["plan_name"] == "Dominant"
    assert items[0]["territory"] == "EUROPE"
    assert items[1]["status"] == "EXPIRED"
    assert "auth_user_id" not in items[0]
    assert "email" not in items[0]


def test_does_not_leak_other_users_policies_despite_shared_email(policy_api):
    client, authenticate, _, other_id, _ = policy_api
    authenticate(other_id)

    response = client.get(POLICIES_URL)

    assert response.status_code == 200
    items = response.json()
    assert [item["policy_number"] for item in items] == ["OTHER-POLICY"]


def test_returns_empty_list_for_user_without_policies(policy_api):
    client, authenticate, _, _, empty_id = policy_api
    authenticate(empty_id)

    response = client.get(POLICIES_URL)

    assert response.status_code == 200
    assert response.json() == []
