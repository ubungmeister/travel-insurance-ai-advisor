from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.insured_person import InsuredPerson
    from app.models.insurance_terms_version import InsuranceTermsVersion
    from app.models.plan_variant import PlanVariant
    from app.models.user import User


class PolicyStatus(StrEnum):
    ISSUED = "ISSUED"
    CANCELLED = "CANCELLED"


class TripPurpose(StrEnum):
    VACATION = "VACATION"
    WORK_MANUAL = "WORK_MANUAL"
    WORK_NON_MANUAL = "WORK_NON_MANUAL"


class SportCategory(StrEnum):
    RECREATIONAL = "RECREATIONAL"
    WINTER = "WINTER"
    RISKY = "RISKY"


class Policy(Base):
    __tablename__ = "policies"
    __table_args__ = (
        UniqueConstraint(
            "policy_number",
            name="uq_policies_policy_number",
        ),
        UniqueConstraint("user_id", "id", name="uq_policies_user_id_id"),
        CheckConstraint(
            "end_date >= start_date",
            name="ck_policy_valid_date_range",
        ),
        CheckConstraint(
            "trip_purpose IN ('VACATION', 'WORK_MANUAL', 'WORK_NON_MANUAL')",
            name="ck_policy_valid_trip_purpose",
        ),
        CheckConstraint(
            "declared_sport_category IN ('RECREATIONAL', 'WINTER', 'RISKY')",
            name="ck_policy_valid_declared_sport_category",
        ),
        CheckConstraint(
            "price_paid >= 0",
            name="ck_policy_non_negative_price",
        ),
        CheckConstraint(
            "status IN ('ISSUED', 'CANCELLED')",
            name="ck_policy_valid_status",
        ),
        Index(
            "ix_policies_user_status_dates",
            "user_id",
            "status",
            "start_date",
            "end_date",
        ),
        Index(
            "ix_policies_plan_variant_id",
            "plan_variant_id",
        ),
        Index(
            "ix_policies_terms_version_id",
            "terms_version_id",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    policy_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    plan_variant_id: Mapped[int] = mapped_column(
        ForeignKey("plan_variants.id"),
        nullable=False,
    )

    terms_version_id: Mapped[int] = mapped_column(
        ForeignKey("insurance_terms_versions.id"),
        nullable=False,
    )

    trip_purpose: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    declared_sport_category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    end_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    price_paid: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="policies",
    )

    plan_variant: Mapped["PlanVariant"] = relationship(
        back_populates="policies",
    )

    terms_version: Mapped["InsuranceTermsVersion"] = relationship(
        back_populates="policies",
    )

    insured_people: Mapped[list["InsuredPerson"]] = relationship(
        back_populates="policy",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
