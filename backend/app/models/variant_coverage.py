from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.coverage_type import CoverageType
    from app.models.plan_variant import PlanVariant


class VariantCoverage(Base):
    __tablename__ = "variant_coverages"

    __table_args__ = (
        UniqueConstraint(
            "plan_variant_id",
            "coverage_type_id",
            name="uq_variant_coverage",
        ),
        CheckConstraint(
            "limit_amount >= 0",
            name="ck_variant_coverage_non_negative_limit",
        ),
        Index(
            "ix_variant_coverages_coverage_type_id",
            "coverage_type_id",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    plan_variant_id: Mapped[int] = mapped_column(
        ForeignKey("plan_variants.id"),
        nullable=False,
    )

    coverage_type_id: Mapped[int] = mapped_column(
        ForeignKey("coverage_types.id"),
        nullable=False,
    )

    limit_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    plan_variant: Mapped["PlanVariant"] = relationship(
        back_populates="coverages",
    )

    coverage_type: Mapped["CoverageType"] = relationship(
        back_populates="variant_coverages",
    )
