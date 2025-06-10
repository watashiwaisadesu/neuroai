# src/features/chat/infra/persistence/models/conversation.py

from __future__ import annotations # MUST BE FIRST LINE
import uuid
from typing import List, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import String, Text, Float, ForeignKey, Integer, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infra.persistence.models.sqlalchemy_base import SQLAlchemyBase # Adjust import path

if TYPE_CHECKING:
    from src.features.conversation.infra.persistence.models.message import MessageORM
    # Import other related ORMs if needed for relationships
    # from src.features.identity.infra.persistence.models.platform_user import PlatformUserORM
    # from src.features.bot.infra.persistence.models.bot import BotORM

class ConversationORM(SQLAlchemyBase):
    """ORM Model for Conversations."""
    __tablename__ = "conversations"

    # Foreign keys using internal UUIDs
    owner_uid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.uid"), nullable=False, index=True)
    bot_uid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bots.uid",  ondelete="CASCADE"), nullable=False, index=True)

    # Store platform as String, consider Enum type if DB supports it
    platform: Mapped[str] = mapped_column(String, nullable=False, index=True)
    # Store participant info directly
    sender_id: Mapped[str] = mapped_column(String, nullable=False, index=True) # External ID
    sender_number: Mapped[str | None] = mapped_column(String, nullable=True)
    sender_nickname: Mapped[str | None] = mapped_column(String, nullable=True)

    # Other fields
    bot_name: Mapped[str | None] = mapped_column(String, nullable=True) # Denormalized?
    crm_catalog_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationship to messages
    messages: Mapped[List["MessageORM"]] = relationship(
        "src.features.conversation.infra.persistence.models.message.MessageORM", # Use full path
        back_populates="conversation",

        cascade="all, delete-orphan",
        lazy="selectin", # Or another strategy
        order_by="MessageORM.timestamp" # Keep messages ordered
    )

    # Optional relationships back to owner/bot
    # owner: Mapped["PlatformUserORM"] = relationship(...)
    # bot: Mapped["BotORM"] = relationship(...)

    def __repr__(self) -> str:
        return f"<ConversationORM uid={self.uid} owner={self.owner_uid} bot={self.bot_uid} platform={self.platform}>"


