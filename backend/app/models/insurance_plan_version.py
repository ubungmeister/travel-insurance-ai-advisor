from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.insurance_plan import InsurancePlan
    from app.models.plan_variant import PlanVariant


class InsurancePlanVersion(Base):
    __tablename__ = "insurance_plan_versions"
    __table_args__ = (
        UniqueConstraint(
            "plan_id",
            "version",
            name="uq_insurance_plan_version",
        ),
        CheckConstraint(
            "version > 0",
            name="ck_insurance_plan_version_positive",
        ),
        CheckConstraint(
            "available_to IS NULL OR available_to >= available_from",
            name="ck_insurance_plan_version_availability_dates",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    plan_id: Mapped[int] = mapped_column(
        ForeignKey("insurance_plans.id"),
        nullable=False,
    )

    version: Mapped[int] = mapped_column(
        nullable=False,
    )

    available_from: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    available_to: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    plan: Mapped["InsurancePlan"] = relationship(
        back_populates="versions",
    )

    variants: Mapped[list["PlanVariant"]] = relationship(
        back_populates="plan_version",
    )
