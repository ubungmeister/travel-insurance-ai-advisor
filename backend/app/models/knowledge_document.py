from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.insurance_terms_version import InsuranceTermsVersion


class DocumentProcessingStatus(StrEnum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"
    __table_args__ = (
        CheckConstraint(
            "processing_status IN "
            "('UPLOADED', 'PROCESSING', 'READY', 'FAILED')",
            name="ck_knowledge_document_processing_status",
        ),
        Index(
            "ix_knowledge_documents_terms_version_id",
            "terms_version_id",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    terms_version_id: Mapped[int] = mapped_column(
        ForeignKey("insurance_terms_versions.id"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    storage_path: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        nullable=False,
    )

    checksum: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )

    processing_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=DocumentProcessingStatus.UPLOADED,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    terms_version: Mapped["InsuranceTermsVersion"] = relationship(
        back_populates="knowledge_documents",
    )