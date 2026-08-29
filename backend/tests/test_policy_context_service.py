from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.seed import seed_database
from app.services.policy_context_service import (
    calculate_age,
    list_active_policy_contexts,
)


def test_calculate_age_uses_whether_birthday_has_passed() -> None:
    date_of_birth = date(1990, 5, 15)

    assert calculate_age(date_of_birth, date(2026, 5, 14)) == 35
    assert calculate_age(date_of_birth, date(2026, 5, 15)) == 36


def test_builds_safe_policy_context_from_repository_data() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        seed_database(db)
        db.commit()

        contexts = list_active_policy_contexts(
            db=db,
            user_email="demo@example.com",
            active_on=date(2026, 8, 29),
        )

    assert len(contexts) == 1
    context = contexts[0]
    assert context.plan_name == "Dominant"
    assert context.plan_version == 1
    assert context.territory == "EUROPE"
    assert context.insured_people[0].age == 36
    assert context.insured_people[0].model_dump() == {"age": 36}
    assert len(context.coverages) == 7

    dental = next(
        item for item in context.coverages if item.code == "DENTAL_TREATMENT"
    )
    assert dental.limit_amount == Decimal("10000.00")
    assert dental.currency == "CZK"


def test_returns_no_context_outside_policy_dates() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        seed_database(db)
        db.commit()

        contexts = list_active_policy_contexts(
            db=db,
            user_email="demo@example.com",
            active_on=date(2026, 9, 6),
        )

    assert contexts == []
