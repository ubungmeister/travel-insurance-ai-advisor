"""harden existing insurance models

Revision ID: 4d2a8b7c1e90
Revises: 95cb98197369
Create Date: 2026-09-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4d2a8b7c1e90"
down_revision: Union[str, Sequence[str], None] = "95cb98197369"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_insurance_plan_version_positive",
        "insurance_plan_versions",
        "version > 0",
    )
    op.create_check_constraint(
        "ck_insurance_plan_version_valid_dates",
        "insurance_plan_versions",
        "valid_to IS NULL OR valid_to >= valid_from",
    )

    op.add_column(
        "policies",
        sa.Column("policy_number", sa.String(length=50), nullable=True),
    )
    op.execute(
        "UPDATE policies "
        "SET policy_number = 'POL-' || LPAD(id::text, 8, '0') "
        "WHERE policy_number IS NULL"
    )
    op.alter_column(
        "policies",
        "policy_number",
        existing_type=sa.String(length=50),
        nullable=False,
    )
    op.create_unique_constraint(
        "uq_policies_policy_number",
        "policies",
        ["policy_number"],
    )
    op.alter_column(
        "policies",
        "sport_category",
        new_column_name="declared_sport_category",
        existing_type=sa.String(length=50),
        existing_nullable=False,
    )
    op.add_column(
        "policies",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_check_constraint(
        "ck_policy_valid_date_range",
        "policies",
        "end_date >= start_date",
    )
    op.create_check_constraint(
        "ck_policy_non_negative_price",
        "policies",
        "price_paid >= 0",
    )
    op.create_check_constraint(
        "ck_policy_valid_status",
        "policies",
        "status IN ('ACTIVE', 'EXPIRED', 'CANCELLED')",
    )
    op.create_index(
        "ix_policies_user_status_dates",
        "policies",
        ["user_id", "status", "start_date", "end_date"],
    )
    op.create_index(
        "ix_policies_plan_variant_id",
        "policies",
        ["plan_variant_id"],
    )

    op.create_check_constraint(
        "ck_variant_coverage_non_negative_limit",
        "variant_coverages",
        "limit_amount >= 0",
    )
    op.create_index(
        "ix_variant_coverages_coverage_type_id",
        "variant_coverages",
        ["coverage_type_id"],
    )

    op.drop_constraint(
        "insured_persons_policy_id_fkey",
        "insured_persons",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "insured_persons_policy_id_fkey",
        "insured_persons",
        "policies",
        ["policy_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(
        "ix_insured_persons_policy_id",
        "insured_persons",
        ["policy_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_insured_persons_policy_id",
        table_name="insured_persons",
    )
    op.drop_constraint(
        "insured_persons_policy_id_fkey",
        "insured_persons",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "insured_persons_policy_id_fkey",
        "insured_persons",
        "policies",
        ["policy_id"],
        ["id"],
    )

    op.drop_index(
        "ix_variant_coverages_coverage_type_id",
        table_name="variant_coverages",
    )
    op.drop_constraint(
        "ck_variant_coverage_non_negative_limit",
        "variant_coverages",
        type_="check",
    )

    op.drop_index("ix_policies_plan_variant_id", table_name="policies")
    op.drop_index("ix_policies_user_status_dates", table_name="policies")
    op.drop_constraint(
        "ck_policy_valid_status",
        "policies",
        type_="check",
    )
    op.drop_constraint(
        "ck_policy_non_negative_price",
        "policies",
        type_="check",
    )
    op.drop_constraint(
        "ck_policy_valid_date_range",
        "policies",
        type_="check",
    )
    op.drop_column("policies", "updated_at")
    op.alter_column(
        "policies",
        "declared_sport_category",
        new_column_name="sport_category",
        existing_type=sa.String(length=50),
        existing_nullable=False,
    )
    op.drop_constraint(
        "uq_policies_policy_number",
        "policies",
        type_="unique",
    )
    op.drop_column("policies", "policy_number")

    op.drop_constraint(
        "ck_insurance_plan_version_valid_dates",
        "insurance_plan_versions",
        type_="check",
    )
    op.drop_constraint(
        "ck_insurance_plan_version_positive",
        "insurance_plan_versions",
        type_="check",
    )
