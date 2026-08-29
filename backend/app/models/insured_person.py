from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.policy import Policy


class InsuredPerson(Base):
    __tablename__ = "insured_persons"

    id: Mapped[int] = mapped_column(primary_key=True)

    policy_id: Mapped[int] = mapped_column(
        ForeignKey("policies.id"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    date_of_birth: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    policy: Mapped["Policy"] = relationship(
        back_populates="insured_people",
    )
