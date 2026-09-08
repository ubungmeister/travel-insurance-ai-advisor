from datetime import date

from sqlalchemy.orm import Session

from app.models import Policy
from app.repositories.policy_repository import (
    list_active_policies_by_user_email,
)
from app.schemas.policy_context import (
    CoverageContext,
    InsuredPersonContext,
    PolicyContext,
)


def calculate_age(date_of_birth: date, on_date: date) -> int:
    years = on_date.year - date_of_birth.year
    birthday_has_passed = (on_date.month, on_date.day) >= (
        date_of_birth.month,
        date_of_birth.day,
    )
    return years if birthday_has_passed else years - 1


def build_policy_context(policy: Policy) -> PolicyContext:
    insured_people = [
        InsuredPersonContext(
            age=calculate_age(person.date_of_birth, policy.start_date)
        )
        for person in sorted(policy.insured_people, key=lambda item: item.id)
    ]

    coverages = [
        CoverageContext(
            code=coverage.coverage_type.code,
            name=coverage.coverage_type.name,
            limit_amount=coverage.limit_amount,
            currency=coverage.currency,
        )
        for coverage in sorted(
            policy.plan_variant.coverages,
            key=lambda item: item.coverage_type.code,
        )
    ]

    return PolicyContext(
        policy_id=policy.id,
        plan_name=policy.plan_variant.plan_version.name,
        plan_version=policy.plan_variant.plan_version.version,
        territory=policy.plan_variant.territory,
        trip_purpose=policy.trip_purpose,
        sport_category=policy.declared_sport_category,
        start_date=policy.start_date,
        end_date=policy.end_date,
        insured_people=insured_people,
        coverages=coverages,
    )


def list_active_policy_contexts(
    db: Session,
    user_email: str,
    active_on: date,
) -> list[PolicyContext]:
    policies = list_active_policies_by_user_email(
        db=db,
        user_email=user_email,
        active_on=active_on,
    )
    return [build_policy_context(policy) for policy in policies]
