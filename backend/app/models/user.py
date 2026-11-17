from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.conversation import Conversation
    from app.models.policy import Policy


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    auth_user_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        unique=True,
        nullable=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    policies: Mapped[list["Policy"]] = relationship(
        back_populates="user",
    )

    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="user",
        foreign_keys="Conversation.user_id",
    )
