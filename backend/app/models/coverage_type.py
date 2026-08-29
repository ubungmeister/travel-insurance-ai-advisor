from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.variant_coverage import VariantCoverage


class CoverageType(Base):
    __tablename__ = "coverage_types"

    id: Mapped[int] = mapped_column(primary_key=True)

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    variant_coverages: Mapped[list["VariantCoverage"]] = relationship(
        back_populates="coverage_type",
    )
