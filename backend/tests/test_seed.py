from decimal import Decimal

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.seed import seed_database
from app.models import (
    CoverageType,
    InsurancePlanVersion,
    InsuredPerson,
    PlanVariant,
    Policy,
    User,
    VariantCoverage,
)


def _count(db: Session, model: type[Base]) -> int:
    return db.scalar(select(func.count()).select_from(model)) or 0


def test_seed_is_idempotent() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        seed_database(db)
        db.commit()

        first_counts = {
            model: _count(db, model)
            for model in (
                CoverageType,
                InsurancePlanVersion,
                PlanVariant,
                VariantCoverage,
                User,
                Policy,
                InsuredPerson,
            )
        }

        seed_database(db)
        db.commit()

        second_counts = {
            model: _count(db, model) for model in first_counts
        }

    assert first_counts == second_counts
    assert first_counts[CoverageType] == 7
    assert first_counts[InsurancePlanVersion] == 4
    assert first_counts[PlanVariant] == 8
    assert first_counts[User] == 1
    assert first_counts[Policy] == 1
    assert first_counts[InsuredPerson] == 1


def test_seed_restores_demo_policy_values() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        seed_database(db)
        db.commit()

        policy = db.scalar(select(Policy))
        assert policy is not None
        policy.trip_purpose = "CHANGED"
        policy.sport_category = "CHANGED"
        policy.status = "CANCELLED"
        policy.price_paid = Decimal("999.00")
        policy.currency = "EUR"
        db.commit()

        seed_database(db)
        db.commit()
        db.refresh(policy)

        assert policy.trip_purpose == "VACATION"
        assert policy.sport_category == "RECREATIONAL"
        assert policy.status == "ACTIVE"
        assert policy.price_paid == Decimal("45.00")
        assert policy.currency == "CZK"
