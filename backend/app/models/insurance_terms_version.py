from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.insurance_plan_version import InsurancePlanVersion
    from app.models.knowledge_document import KnowledgeDocument


class InsuranceTermsVersion(Base):
    __tablename__ = "insurance_terms_versions"
    __table_args__ = (
        UniqueConstraint(
            "code",
            name="uq_insurance_terms_versions_code",
        ),
        CheckConstraint(
            "valid_to IS NULL OR valid_to >= valid_from",
            name="ck_insurance_terms_version_valid_dates",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    valid_from: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    valid_to: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    plan_versions: Mapped[list["InsurancePlanVersion"]] = relationship(
        back_populates="terms_version",
    )

    knowledge_documents: Mapped[list["KnowledgeDocument"]] = relationship(
        back_populates="terms_version",
    )
