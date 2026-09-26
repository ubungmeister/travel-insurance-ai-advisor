"""extract insurance plan name into insurance_plans table

Revision ID: d8a1f4c62b95
Revises: b6d4e21f9a37
Create Date: 2026-09-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d8a1f4c62b95"
down_revision: Union[str, Sequence[str], None] = "b6d4e21f9a37"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "insurance_plans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_insurance_plans_name"),
    )

    op.add_column(
        "insurance_plan_versions",
        sa.Column("plan_id", sa.Integer(), nullable=True),
    )
    op.execute(
        "INSERT INTO insurance_plans (name) "
        "SELECT DISTINCT name FROM insurance_plan_versions"
    )
    op.execute(
        "UPDATE insurance_plan_versions ipv "
        "SET plan_id = ip.id "
        "FROM insurance_plans ip "
        "WHERE ip.name = ipv.name"
    )
    op.alter_column(
        "insurance_plan_versions",
        "plan_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.create_foreign_key(
        "insurance_plan_versions_plan_id_fkey",
        "insurance_plan_versions",
        "insurance_plans",
        ["plan_id"],
        ["id"],
    )
    op.drop_constraint(
        "uq_insurance_plan_version",
        "insurance_plan_versions",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_insurance_plan_version",
        "insurance_plan_versions",
        ["plan_id", "version"],
    )
    op.drop_column("insurance_plan_versions", "name")


def downgrade() -> None:
    op.add_column(
        "insurance_plan_versions",
        sa.Column("name", sa.String(length=50), nullable=True),
    )
    op.execute(
        "UPDATE insurance_plan_versions ipv "
        "SET name = ip.name "
        "FROM insurance_plans ip "
        "WHERE ip.id = ipv.plan_id"
    )
    op.alter_column(
        "insurance_plan_versions",
        "name",
        existing_type=sa.String(length=50),
        nullable=False,
    )
    op.drop_constraint(
        "uq_insurance_plan_version",
        "insurance_plan_versions",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_insurance_plan_version",
        "insurance_plan_versions",
        ["name", "version"],
    )
    op.drop_constraint(
        "insurance_plan_versions_plan_id_fkey",
        "insurance_plan_versions",
        type_="foreignkey",
    )
    op.drop_column("insurance_plan_versions", "plan_id")
    op.drop_table("insurance_plans")
