from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.policy_context import (
    CoverageContext,
    InsuredPersonContext,
    PolicyContext,
)


def test_policy_context_contains_only_rag_fields() -> None:
    context = PolicyContext(
        policy_id=1,
        plan_name="Dominant",
        plan_version=1,
        territory="EUROPE",
        trip_purpose="VACATION",
        sport_category="RECREATIONAL",
        start_date=date(2026, 8, 26),
        end_date=date(2026, 9, 5),
        insured_people=[InsuredPersonContext(age=36)],
        coverages=[
            CoverageContext(
                code="DENTAL_TREATMENT",
                name="Emergency dental treatment",
                limit_amount=Decimal("10000.00"),
                currency="CZK",
            )
        ],
    )

    assert context.plan_name == "Dominant"
    assert context.insured_people[0].age == 36
    assert context.coverages[0].limit_amount == Decimal("10000.00")


def test_policy_context_rejects_unexpected_personal_data() -> None:
    with pytest.raises(ValidationError):
        PolicyContext(
            policy_id=1,
            plan_name="Dominant",
            plan_version=1,
            territory="EUROPE",
            trip_purpose="VACATION",
            sport_category="RECREATIONAL",
            start_date=date(2026, 8, 26),
            end_date=date(2026, 9, 5),
            insured_people=[InsuredPersonContext(age=36)],
            coverages=[],
            email="demo@example.com",
        )
