"""narrow policy status values

Revision ID: b6d4e21f9a37
Revises: c2a7d8e91f04
Create Date: 2026-09-26

"""
from typing import Sequence, Union

from alembic import op


revision: str = "b6d4e21f9a37"
down_revision: Union[str, Sequence[str], None] = "c2a7d8e91f04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_policy_valid_status", "policies", type_="check")
    op.execute("UPDATE policies SET status = 'ISSUED' WHERE status != 'CANCELLED'")
    op.create_check_constraint(
        "ck_policy_valid_status",
        "policies",
        "status IN ('ISSUED', 'CANCELLED')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_policy_valid_status", "policies", type_="check")
    op.execute("UPDATE policies SET status = 'ACTIVE' WHERE status = 'ISSUED'")
    op.create_check_constraint(
        "ck_policy_valid_status",
        "policies",
        "status IN ('ACTIVE', 'PENDING', 'EXPIRED', 'CANCELLED', 'LAPSED')",
    )
