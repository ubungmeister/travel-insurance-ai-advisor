from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.policy_repository import list_policies_by_auth_user_id
from app.schemas.policy import PolicySummary


def list_user_policies(db: Session, auth_user_id: UUID) -> list[PolicySummary]:
    policies = list_policies_by_auth_user_id(db, auth_user_id)
    return [
        PolicySummary(
            policy_id=policy.id,
            policy_number=policy.policy_number,
            plan_name=policy.plan_variant.plan_version.name,
            plan_version=policy.plan_variant.plan_version.version,
            territory=policy.plan_variant.territory,
            trip_purpose=policy.trip_purpose,
            sport_category=policy.declared_sport_category,
            start_date=policy.start_date,
            end_date=policy.end_date,
            status=policy.status,
        )
        for policy in policies
    ]
