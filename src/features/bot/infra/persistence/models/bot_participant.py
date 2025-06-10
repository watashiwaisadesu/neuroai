# src/features/bot/infra/persistence/models/bot_participant.py

from __future__ import annotations # MUST BE FIRST LINE

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infra.persistence.models.sqlalchemy_base import SQLAlchemyBase

# Use TYPE_CHECKING to avoid runtime circular imports if needed for type hints
if TYPE_CHECKING:
    from src.features.bot.infra.persistence.models.bot import BotORM
    from src.features.identity.infra.persistence.models.user import UserORM


class BotParticipantORM(SQLAlchemyBase):
    """SQLAlchemy ORM model for Bot Participants."""
    __tablename__ = "bot_participants"


    bot_uid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bots.uid", ondelete="CASCADE"), nullable=False, index=True)
    user_uid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.uid", ondelete="CASCADE"), nullable=False, index=True)

    role: Mapped[str] = mapped_column(String(50), nullable=False, default="viewer")

    bot: Mapped[BotORM] = relationship(
        "src.features.bot.infra.persistence.models.bot.BotORM",
        back_populates="bot_participants"
    )

    user: Mapped[UserORM] = relationship(
        "src.features.identity.infra.persistence.models.user.UserORM",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<BotParticipant bot={self.bot_uid} user={self.user_uid} role='{self.role}'>"

