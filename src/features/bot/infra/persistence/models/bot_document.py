# src/features/bot/infra/persistence/models/bot_document.py (New file)

from __future__ import annotations  # MUST BE FIRST LINE
import uuid
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, ForeignKey, LargeBinary, Integer  # Import LargeBinary for file_data
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infra.persistence.models.sqlalchemy_base import SQLAlchemyBase  # Adjust import path

if TYPE_CHECKING:
    from src.features.bot.infra.persistence.models.bot import BotORM


class BotDocumentORM(SQLAlchemyBase):
    """SQLAlchemy ORM model for Bot Documents."""
    __tablename__ = "bot_documents"

    # uid, created_at, updated_at inherited from SQLAlchemyBase

    bot_uid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bots.uid", ondelete="CASCADE"),  # Cascade delete if bot is deleted
        nullable=False,
        index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Option 1: Store file data directly (as in your example)
    file_data: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    # Option 2: Store reference
    # storage_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    # file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationship back to the bot
    bot: Mapped["BotORM"] = relationship(
        "src.features.bot.infra.persistence.models.bot.BotORM",
        back_populates="documents"  # Ensure BotORM has 'documents' relationship
    )

    def __repr__(self) -> str:
        return f"<BotDocumentORM uid={self.uid} filename='{self.filename}' bot_uid={self.bot_uid}>"
