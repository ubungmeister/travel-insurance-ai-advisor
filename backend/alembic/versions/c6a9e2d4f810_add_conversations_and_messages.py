"""add conversations and messages

Revision ID: c6a9e2d4f810
Revises: b7d2f3a9c1e6
Create Date: 2026-11-17
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c6a9e2d4f810"
down_revision: Union[str, Sequence[str], None] = "b7d2f3a9c1e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_policies_user_id_id", "policies", ["user_id", "id"]
    )
    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("selected_policy_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(
            ["user_id", "selected_policy_id"],
            ["policies.user_id", "policies.id"],
            name="fk_conversation_policy_owner",
        ),
    )
    op.create_index("ix_conversations_user_id", "conversations", ["user_id"])
    op.create_index(
        "ix_conversations_policy_owner",
        "conversations",
        ["user_id", "selected_policy_id"],
    )
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"], ["conversations.id"], ondelete="CASCADE"
        ),
        sa.CheckConstraint(
            "role IN ('USER', 'ASSISTANT')", name="ck_message_valid_role"
        ),
        sa.CheckConstraint(
            "length(trim(content)) > 0", name="ck_message_non_empty_content"
        ),
    )
    op.create_index(
        "ix_messages_conversation_id_id", "messages", ["conversation_id", "id"]
    )


def downgrade() -> None:
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_constraint("uq_policies_user_id_id", "policies", type_="unique")
