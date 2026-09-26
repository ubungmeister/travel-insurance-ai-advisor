from typing import TYPE_CHECKING

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.insurance_plan_version import InsurancePlanVersion


class InsurancePlan(Base):
    __tablename__ = "insurance_plans"
    __table_args__ = (
        UniqueConstraint(
            "name",
            name="uq_insurance_plans_name",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    versions: Mapped[list["InsurancePlanVersion"]] = relationship(
        back_populates="plan",
    )
