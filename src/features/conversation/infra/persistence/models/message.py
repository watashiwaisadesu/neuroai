
# src/features/chat/infra/persistence/models/message.py

from __future__ import annotations # MUST BE FIRST LINE
import uuid
from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func # For server_default timestamp

from src.infra.persistence.models.sqlalchemy_base import SQLAlchemyBase # Adjust import path

if TYPE_CHECKING:
    from src.features.conversation.infra.persistence.models.conversation import ConversationORM

class MessageORM(SQLAlchemyBase):
    """ORM Model for Messages."""
    __tablename__ = "messages"

    # Foreign key to Conversation ORM using internal UID
    conversation_uid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("conversations.uid"), nullable=False, index=True)

    # Store role as String, consider Enum type if DB supports it
    role: Mapped[str] = mapped_column(String, nullable=False) # "user", "assistant", "system"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True) # Use timezone-aware timestamp, default in DB
    tokens_user: Mapped[int | None] = mapped_column(Integer, default=0, nullable=True)
    tokens_ai: Mapped[int | None] = mapped_column(Integer, default=0, nullable=True)

    # Relationship back to conversation
    conversation: Mapped["ConversationORM"] = relationship(
        "src.features.conversation.infra.persistence.models.conversation.ConversationORM", # Use full path
        back_populates="messages"
    )

    def __repr__(self) -> str:
        return f"<MessageORM uid={self.uid} role={self.role} convo_uid={self.conversation_uid}>"
