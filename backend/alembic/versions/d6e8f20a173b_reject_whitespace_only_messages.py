"""reject whitespace-only messages

Revision ID: d6e8f20a173b
Revises: c6a9e2d4f810
Create Date: 2026-11-17
"""
from typing import Sequence, Union

from alembic import op


revision: str = "d6e8f20a173b"
down_revision: Union[str, Sequence[str], None] = "c6a9e2d4f810"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_message_non_empty_content", "messages", type_="check")
    op.create_check_constraint(
        "ck_message_non_empty_content",
        "messages",
        "length(trim(content, ' \t\n\r\v\f')) > 0",
    )


def downgrade() -> None:
    op.drop_constraint("ck_message_non_empty_content", "messages", type_="check")
    op.create_check_constraint(
        "ck_message_non_empty_content",
        "messages",
        "length(trim(content)) > 0",
    )
