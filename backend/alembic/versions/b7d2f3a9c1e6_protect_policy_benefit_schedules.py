"""protect benefit schedules referenced by policies

Revision ID: b7d2f3a9c1e6
Revises: e91a6c4b7d20
Create Date: 2026-11-17
"""
from typing import Sequence, Union

from alembic import op


revision: str = "b7d2f3a9c1e6"
down_revision: Union[str, Sequence[str], None] = "e91a6c4b7d20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE FUNCTION prevent_issued_variant_coverage_mutation()
        RETURNS trigger AS $$
        BEGIN
            IF TG_OP = 'UPDATE' THEN
                PERFORM id
                FROM plan_variants
                WHERE id IN (OLD.plan_variant_id, NEW.plan_variant_id)
                ORDER BY id
                FOR UPDATE;

                IF EXISTS (
                    SELECT 1
                    FROM policies
                    WHERE plan_variant_id IN (OLD.plan_variant_id, NEW.plan_variant_id)
                ) THEN
                    RAISE EXCEPTION
                        'Coverage schedules referenced by policies are immutable';
                END IF;
                RETURN NEW;
            ELSIF TG_OP = 'DELETE' THEN
                PERFORM id
                FROM plan_variants
                WHERE id = OLD.plan_variant_id
                FOR UPDATE;

                IF EXISTS (
                    SELECT 1
                    FROM policies
                    WHERE plan_variant_id = OLD.plan_variant_id
                ) THEN
                    RAISE EXCEPTION
                        'Coverage schedules referenced by policies are immutable';
                END IF;
                RETURN OLD;
            ELSE
                PERFORM id
                FROM plan_variants
                WHERE id = NEW.plan_variant_id
                FOR UPDATE;

                IF EXISTS (
                    SELECT 1
                    FROM policies
                    WHERE plan_variant_id = NEW.plan_variant_id
                ) THEN
                    RAISE EXCEPTION
                        'Coverage schedules referenced by policies are immutable';
                END IF;
                RETURN NEW;
            END IF;
        END;
        $$ LANGUAGE plpgsql
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_prevent_issued_variant_coverage_mutation
        BEFORE INSERT OR UPDATE OR DELETE ON variant_coverages
        FOR EACH ROW
        EXECUTE FUNCTION prevent_issued_variant_coverage_mutation()
        """
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER trg_prevent_issued_variant_coverage_mutation "
        "ON variant_coverages"
    )
    op.execute("DROP FUNCTION prevent_issued_variant_coverage_mutation()")
