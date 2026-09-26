"""add knowledge documents

Revision ID: a4e91c7f5b28
Revises: f2c6b8a13d70
Create Date: 2026-09-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a4e91c7f5b28"
down_revision: Union[str, Sequence[str], None] = "f2c6b8a13d70"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "knowledge_documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("terms_version_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("storage_path", sa.String(length=500), nullable=False),
        sa.Column("checksum", sa.String(length=64), nullable=False),
        sa.Column("processing_status", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["terms_version_id"], ["insurance_terms_versions.id"]
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("storage_path"),
        sa.UniqueConstraint("checksum"),
        sa.CheckConstraint(
            "processing_status IN ('UPLOADED', 'PROCESSING', 'READY', 'FAILED')",
            name="ck_knowledge_document_processing_status",
        ),
    )
    op.create_index(
        "ix_knowledge_documents_terms_version_id",
        "knowledge_documents",
        ["terms_version_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_knowledge_documents_terms_version_id",
        table_name="knowledge_documents",
    )
    op.drop_table("knowledge_documents")
