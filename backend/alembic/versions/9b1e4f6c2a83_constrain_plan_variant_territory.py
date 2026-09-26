"""constrain plan variant territory values

Revision ID: 9b1e4f6c2a83
Revises: 7f3c1a9d5e42
Create Date: 2026-09-19

"""
from typing import Sequence, Union

from alembic import op


revision: str = "9b1e4f6c2a83"
down_revision: Union[str, Sequence[str], None] = "7f3c1a9d5e42"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "UPDATE plan_variants SET territory = 'CZECH_REPUBLIC' "
        "WHERE territory = 'DOMESTIC'"
    )
    op.create_check_constraint(
        "ck_plan_variant_valid_territory",
        "plan_variants",
        "territory IN ('EUROPE', 'WORLD', 'CZECH_REPUBLIC')",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_plan_variant_valid_territory", "plan_variants", type_="check"
    )
    op.execute(
        "UPDATE plan_variants SET territory = 'DOMESTIC' "
        "WHERE territory = 'CZECH_REPUBLIC'"
    )
