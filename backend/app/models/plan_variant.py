from typing import TYPE_CHECKING
from enum import StrEnum

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.insurance_plan_version import InsurancePlanVersion
    from app.models.policy import Policy
    from app.models.variant_coverage import VariantCoverage


class Territory(StrEnum):
    EUROPE = "EUROPE"
    WORLD = "WORLD"
    CZECH_REPUBLIC = "CZECH_REPUBLIC"


class SportCategory(StrEnum):
    RECREATIONAL = "RECREATIONAL"
    WINTER = "WINTER"
    RISKY = "RISKY"


class PlanVariant(Base):
    __tablename__ = "plan_variants"
    __table_args__ = (
        UniqueConstraint(
            "plan_version_id",
            "territory",
            "sport_category",
            name="uq_plan_variant_identity",
            postgresql_nulls_not_distinct=True,
        ),
        CheckConstraint(
            "territory IN ('EUROPE', 'WORLD', 'CZECH_REPUBLIC')",
            name="ck_plan_variant_valid_territory",
        ),
        CheckConstraint(
            "sport_category IS NULL OR sport_category IN ('RECREATIONAL', 'WINTER', 'RISKY')",
            name="ck_plan_variant_valid_sport_category",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    plan_version_id: Mapped[int] = mapped_column(
        ForeignKey("insurance_plan_versions.id"),
        nullable=False,
    )

    territory: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    sport_category: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    plan_version: Mapped["InsurancePlanVersion"] = relationship(
        back_populates="variants",
    )

    policies: Mapped[list["Policy"]] = relationship(
        back_populates="plan_variant",
    )

    coverages: Mapped[list["VariantCoverage"]] = relationship(
        back_populates="plan_variant",
    )
