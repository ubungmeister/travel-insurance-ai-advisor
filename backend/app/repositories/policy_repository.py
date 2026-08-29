from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models import PlanVariant, Policy, User, VariantCoverage


def list_active_policies_by_user_email(
    db: Session,
    user_email: str,
    active_on: date,
) -> list[Policy]:
    """Return active policies and all data needed to build policy context."""
    statement = (
        select(Policy)
        .join(Policy.user)
        .where(
            User.email == user_email,
            Policy.status == "ACTIVE",
            Policy.start_date <= active_on,
            Policy.end_date >= active_on,
        )
        .options(
            joinedload(Policy.user),
            joinedload(Policy.plan_variant).joinedload(
                PlanVariant.plan_version
            ),
            joinedload(Policy.plan_variant)
            .selectinload(PlanVariant.coverages)
            .joinedload(VariantCoverage.coverage_type),
            selectinload(Policy.insured_people),
        )
        .order_by(Policy.start_date.desc(), Policy.id.desc())
    )

    return list(db.scalars(statement).unique().all())
