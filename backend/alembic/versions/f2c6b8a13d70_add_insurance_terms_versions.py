"""add insurance terms versions

Revision ID: f2c6b8a13d70
Revises: d8a1f4c62b95
Create Date: 2026-09-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f2c6b8a13d70"
down_revision: Union[str, Sequence[str], None] = "d8a1f4c62b95"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "insurance_terms_versions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("valid_from", sa.Date(), nullable=False),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_insurance_terms_versions_code"),
        sa.CheckConstraint(
            "valid_to IS NULL OR valid_to >= valid_from",
            name="ck_insurance_terms_version_valid_dates",
        ),
    )

    op.add_column(
        "insurance_plan_versions",
        sa.Column("terms_version_id", sa.Integer(), nullable=True),
    )
    op.execute(
        "INSERT INTO insurance_terms_versions (code, valid_from, valid_to) "
        "VALUES ('VPP_CP_2021', '2021-04-01', NULL)"
    )
    op.execute(
        "UPDATE insurance_plan_versions "
        "SET terms_version_id = (SELECT id FROM insurance_terms_versions WHERE code = 'VPP_CP_2021')"
    )
    op.alter_column(
        "insurance_plan_versions",
        "terms_version_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.create_foreign_key(
        "insurance_plan_versions_terms_version_id_fkey",
        "insurance_plan_versions",
        "insurance_terms_versions",
        ["terms_version_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "insurance_plan_versions_terms_version_id_fkey",
        "insurance_plan_versions",
        type_="foreignkey",
    )
    op.drop_column("insurance_plan_versions", "terms_version_id")
    op.drop_table("insurance_terms_versions")
