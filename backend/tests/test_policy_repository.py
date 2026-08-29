from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.seed import seed_database
from app.repositories.policy_repository import (
    list_active_policies_by_user_email,
)


def test_loads_complete_active_policy_context() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        seed_database(db)
        db.commit()

        policies = list_active_policies_by_user_email(
            db,
            user_email="demo@example.com",
            active_on=date(2026, 8, 29),
        )

        assert len(policies) == 1
        policy = policies[0]
        assert policy.user.email == "demo@example.com"
        assert policy.plan_variant.territory == "EUROPE"
        assert policy.plan_variant.plan_version.name == "Dominant"
        assert [person.name for person in policy.insured_people] == [
            "Demo User"
        ]

        limits = {
            coverage.coverage_type.code: coverage.limit_amount
            for coverage in policy.plan_variant.coverages
        }
        assert limits["DENTAL_TREATMENT"] == Decimal("10000.00")
        assert limits["MEDICAL_EXPENSES"] == Decimal("15000000.00")


def test_excludes_policy_outside_coverage_dates() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        seed_database(db)
        db.commit()

        policies = list_active_policies_by_user_email(
            db,
            user_email="demo@example.com",
            active_on=date(2026, 9, 6),
        )

        assert policies == []
