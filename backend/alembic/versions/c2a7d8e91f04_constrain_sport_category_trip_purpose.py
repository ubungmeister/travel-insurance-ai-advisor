"""constrain sport category and trip purpose values

Revision ID: c2a7d8e91f04
Revises: 9b1e4f6c2a83
Create Date: 2026-09-19

"""
from typing import Sequence, Union

from alembic import op


revision: str = "c2a7d8e91f04"
down_revision: Union[str, Sequence[str], None] = "9b1e4f6c2a83"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename the old combined tier in place, then clone it as a separate RISKY variant.
    op.execute(
        "UPDATE plan_variants SET sport_category = 'WINTER' "
        "WHERE sport_category = 'WINTER_OR_RISKY'"
    )
    op.execute(
        "INSERT INTO plan_variants (plan_version_id, territory, sport_category) "
        "SELECT plan_version_id, territory, 'RISKY' "
        "FROM plan_variants "
        "WHERE territory = 'CZECH_REPUBLIC' AND sport_category = 'WINTER'"
    )
    op.execute(
        "INSERT INTO variant_coverages (plan_variant_id, coverage_type_id, limit_amount, currency) "
        "SELECT risky.id, vc.coverage_type_id, vc.limit_amount, vc.currency "
        "FROM variant_coverages vc "
        "JOIN plan_variants winter "
        "  ON vc.plan_variant_id = winter.id "
        " AND winter.territory = 'CZECH_REPUBLIC' "
        " AND winter.sport_category = 'WINTER' "
        "JOIN plan_variants risky "
        "  ON risky.plan_version_id = winter.plan_version_id "
        " AND risky.territory = winter.territory "
        " AND risky.sport_category = 'RISKY'"
    )

    op.create_check_constraint(
        "ck_plan_variant_valid_sport_category",
        "plan_variants",
        "sport_category IS NULL OR sport_category IN ('RECREATIONAL', 'WINTER', 'RISKY')",
    )
    op.create_check_constraint(
        "ck_policy_valid_trip_purpose",
        "policies",
        "trip_purpose IN ('VACATION', 'WORK_MANUAL', 'WORK_NON_MANUAL')",
    )
    op.create_check_constraint(
        "ck_policy_valid_declared_sport_category",
        "policies",
        "declared_sport_category IN ('RECREATIONAL', 'WINTER', 'RISKY')",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_policy_valid_declared_sport_category", "policies", type_="check"
    )
    op.drop_constraint("ck_policy_valid_trip_purpose", "policies", type_="check")
    op.drop_constraint(
        "ck_plan_variant_valid_sport_category", "plan_variants", type_="check"
    )

    op.execute(
        "DELETE FROM variant_coverages WHERE plan_variant_id IN ("
        "SELECT id FROM plan_variants "
        "WHERE territory = 'CZECH_REPUBLIC' AND sport_category = 'RISKY')"
    )
    op.execute(
        "DELETE FROM plan_variants "
        "WHERE territory = 'CZECH_REPUBLIC' AND sport_category = 'RISKY'"
    )
    op.execute(
        "UPDATE plan_variants SET sport_category = 'WINTER_OR_RISKY' "
        "WHERE sport_category = 'WINTER'"
    )
