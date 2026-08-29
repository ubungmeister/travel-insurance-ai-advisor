"""add product natural key constraints

Revision ID: c4e8f7a2d6b1
Revises: 938edabac0a9
Create Date: 2026-08-29

"""
from typing import Sequence, Union

from alembic import op


revision: str = "c4e8f7a2d6b1"
down_revision: Union[str, Sequence[str], None] = "938edabac0a9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_insurance_plan_version",
        "insurance_plan_versions",
        ["name", "version"],
    )
    op.create_unique_constraint(
        "uq_plan_variant_identity",
        "plan_variants",
        ["plan_version_id", "territory", "sport_category"],
        postgresql_nulls_not_distinct=True,
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_plan_variant_identity",
        "plan_variants",
        type_="unique",
    )
    op.drop_constraint(
        "uq_insurance_plan_version",
        "insurance_plan_versions",
        type_="unique",
    )
