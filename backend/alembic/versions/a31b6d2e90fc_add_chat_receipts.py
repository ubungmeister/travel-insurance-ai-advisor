"""Add durable per-user chat request receipts."""

import sqlalchemy as sa
from alembic import op

revision = "a31b6d2e90fc"
down_revision = "d6e8f20a173b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "chat_receipts",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("request_id", sa.Uuid(), primary_key=True),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("conversation_id", sa.Integer(), sa.ForeignKey("conversations.id", ondelete="SET NULL")),
        sa.Column("user_message_id", sa.Integer(), sa.ForeignKey("messages.id", ondelete="SET NULL")),
        sa.Column("assistant_message_id", sa.Integer(), sa.ForeignKey("messages.id", ondelete="SET NULL")),
    )


def downgrade():
    op.drop_table("chat_receipts")
