"""expand policy status values

Revision ID: 7f3c1a9d5e42
Revises: 4d2a8b7c1e90
Create Date: 2026-09-19

"""
from typing import Sequence, Union

from alembic import op


revision: str = "7f3c1a9d5e42"
down_revision: Union[str, Sequence[str], None] = "4d2a8b7c1e90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_policy_valid_status", "policies", type_="check")
    op.create_check_constraint(
        "ck_policy_valid_status",
        "policies",
        "status IN ('ACTIVE', 'PENDING', 'EXPIRED', 'CANCELLED', 'LAPSED')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_policy_valid_status", "policies", type_="check")
    op.create_check_constraint(
        "ck_policy_valid_status",
        "policies",
        "status IN ('ACTIVE', 'EXPIRED', 'CANCELLED')",
    )
