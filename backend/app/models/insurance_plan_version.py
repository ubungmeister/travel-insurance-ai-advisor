from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.plan_variant import PlanVariant


class InsurancePlanVersion(Base):
    __tablename__ = "insurance_plan_versions"
    __table_args__ = (
        UniqueConstraint(
            "name",
            "version",
            name="uq_insurance_plan_version",
        ),
        CheckConstraint(
            "version > 0",
            name="ck_insurance_plan_version_positive",
        ),
        CheckConstraint(
            "valid_to IS NULL OR valid_to >= valid_from",
            name="ck_insurance_plan_version_valid_dates",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    version: Mapped[int] = mapped_column(
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

    variants: Mapped[list["PlanVariant"]] = relationship(
        back_populates="plan_version",
    )
