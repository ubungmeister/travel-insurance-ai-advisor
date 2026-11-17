from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, ForeignKeyConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.message import Message
    from app.models.policy import Policy
    from app.models.user import User


class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id", "selected_policy_id"],
            ["policies.user_id", "policies.id"],
            name="fk_conversation_policy_owner",
        ),
        Index("ix_conversations_user_id", "user_id"),
        Index(
            "ix_conversations_policy_owner",
            "user_id",
            "selected_policy_id",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    selected_policy_id: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(
        back_populates="conversations", foreign_keys=[user_id]
    )
    selected_policy: Mapped["Policy | None"] = relationship(
        foreign_keys=[selected_policy_id]
    )
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Message.id",
    )
