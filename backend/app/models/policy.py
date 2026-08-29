from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.insured_person import InsuredPerson
    from app.models.plan_variant import PlanVariant
    from app.models.user import User


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    plan_variant_id: Mapped[int] = mapped_column(
        ForeignKey("plan_variants.id"),
        nullable=False,
    )

    trip_purpose: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    sport_category: Mapped[str] = mapped_column(
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

    user: Mapped["User"] = relationship(
        back_populates="policies",
    )

    plan_variant: Mapped["PlanVariant"] = relationship(
        back_populates="policies",
    )

    insured_people: Mapped[list["InsuredPerson"]] = relationship(
        back_populates="policy",
    )
