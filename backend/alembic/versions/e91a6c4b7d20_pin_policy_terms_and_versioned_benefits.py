"""pin policy terms and version benefit schedules

Revision ID: e91a6c4b7d20
Revises: a4e91c7f5b28
Create Date: 2026-11-17
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e91a6c4b7d20"
down_revision: Union[str, Sequence[str], None] = "a4e91c7f5b28"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Preserve the wording already associated with each existing plan release.
    op.add_column(
        "policies",
        sa.Column("terms_version_id", sa.Integer(), nullable=True),
    )
    op.execute(
        "UPDATE policies p "
        "SET terms_version_id = ipv.terms_version_id "
        "FROM plan_variants pv "
        "JOIN insurance_plan_versions ipv ON ipv.id = pv.plan_version_id "
        "WHERE p.plan_variant_id = pv.id"
    )
    op.alter_column(
        "policies",
        "terms_version_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.create_foreign_key(
        "policies_terms_version_id_fkey",
        "policies",
        "insurance_terms_versions",
        ["terms_version_id"],
        ["id"],
    )
    op.create_index(
        "ix_policies_terms_version_id",
        "policies",
        ["terms_version_id"],
    )

    # created_at is the closest available historical issuance timestamp.
    op.add_column(
        "policies",
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute("UPDATE policies SET issued_at = created_at WHERE issued_at IS NULL")
    op.alter_column(
        "policies",
        "issued_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )

    op.drop_constraint(
        "insurance_plan_versions_terms_version_id_fkey",
        "insurance_plan_versions",
        type_="foreignkey",
    )
    op.drop_column("insurance_plan_versions", "terms_version_id")

    # These dates describe when a release may be issued, not the trip dates.
    op.drop_constraint(
        "ck_insurance_plan_version_valid_dates",
        "insurance_plan_versions",
        type_="check",
    )
    op.alter_column(
        "insurance_plan_versions",
        "valid_from",
        new_column_name="available_from",
        existing_type=sa.Date(),
        existing_nullable=False,
    )
    op.alter_column(
        "insurance_plan_versions",
        "valid_to",
        new_column_name="available_to",
        existing_type=sa.Date(),
        existing_nullable=True,
    )
    op.create_check_constraint(
        "ck_insurance_plan_version_availability_dates",
        "insurance_plan_versions",
        "available_to IS NULL OR available_to >= available_from",
    )

    # Sport no longer selects a benefit schedule. Collapse legacy variants by
    # plan version and territory, preferring recreational when old schedules
    # disagree. Policy sport declarations remain unchanged.
    op.drop_constraint(
        "uq_plan_variant_identity",
        "plan_variants",
        type_="unique",
    )
    op.execute(
        """
        CREATE TEMPORARY TABLE plan_variant_merge_map ON COMMIT DROP AS
        SELECT
            id AS old_id,
            FIRST_VALUE(id) OVER (
                PARTITION BY plan_version_id, territory
                ORDER BY
                    CASE
                        WHEN sport_category = 'RECREATIONAL' THEN 0
                        WHEN sport_category IS NULL THEN 1
                        WHEN sport_category = 'WINTER' THEN 2
                        WHEN sport_category = 'RISKY' THEN 3
                        ELSE 4
                    END,
                    id
            ) AS keep_id
        FROM plan_variants
        """
    )
    op.execute(
        """
        WITH ranked_missing_coverages AS (
            SELECT
                merge_map.keep_id,
                source_coverage.coverage_type_id,
                source_coverage.limit_amount,
                source_coverage.currency,
                ROW_NUMBER() OVER (
                    PARTITION BY merge_map.keep_id, source_coverage.coverage_type_id
                    ORDER BY
                        CASE
                            WHEN source_variant.sport_category = 'RECREATIONAL' THEN 0
                            WHEN source_variant.sport_category IS NULL THEN 1
                            WHEN source_variant.sport_category = 'WINTER' THEN 2
                            WHEN source_variant.sport_category = 'RISKY' THEN 3
                            ELSE 4
                        END,
                        source_variant.id
                ) AS row_number
            FROM plan_variant_merge_map merge_map
            JOIN plan_variants source_variant ON source_variant.id = merge_map.old_id
            JOIN variant_coverages source_coverage
              ON source_coverage.plan_variant_id = source_variant.id
            WHERE merge_map.old_id <> merge_map.keep_id
        )
        INSERT INTO variant_coverages
            (plan_variant_id, coverage_type_id, limit_amount, currency)
        SELECT
            keep_id, coverage_type_id, limit_amount, currency
        FROM ranked_missing_coverages
        WHERE row_number = 1
        ON CONFLICT (plan_variant_id, coverage_type_id) DO NOTHING
        """
    )
    op.execute(
        """
        UPDATE policies p
        SET plan_variant_id = merge_map.keep_id
        FROM plan_variant_merge_map merge_map
        WHERE p.plan_variant_id = merge_map.old_id
          AND merge_map.old_id <> merge_map.keep_id
        """
    )
    op.execute(
        """
        DELETE FROM variant_coverages vc
        USING plan_variant_merge_map merge_map
        WHERE vc.plan_variant_id = merge_map.old_id
          AND merge_map.old_id <> merge_map.keep_id
        """
    )
    op.execute(
        """
        DELETE FROM plan_variants pv
        USING plan_variant_merge_map merge_map
        WHERE pv.id = merge_map.old_id
          AND merge_map.old_id <> merge_map.keep_id
        """
    )
    op.drop_constraint(
        "ck_plan_variant_valid_sport_category",
        "plan_variants",
        type_="check",
    )
    op.drop_column("plan_variants", "sport_category")
    op.create_unique_constraint(
        "uq_plan_variant_identity",
        "plan_variants",
        ["plan_version_id", "territory"],
    )


def downgrade() -> None:
    raise RuntimeError(
        "This migration consolidates sport-specific variants and schedules; "
        "the prior differing coverage amounts cannot be reconstructed."
    )
