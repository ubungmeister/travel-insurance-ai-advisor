from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import PlanVariant, Policy, User


def list_policies_by_auth_user_id(
    db: Session,
    auth_user_id: UUID,
) -> list[Policy]:
    """List only this authenticated customer's policies, regardless of dates."""
    statement = (
        select(Policy)
        .join(Policy.user)
        .where(User.auth_user_id == auth_user_id)
        .options(joinedload(Policy.plan_variant).joinedload(PlanVariant.plan_version))
        .order_by(Policy.start_date.desc(), Policy.id.desc())
    )
    return list(db.scalars(statement).unique().all())
