# src/features/integrations/telegram/infra/persistence/models/telegram_account_link_orm.py (New file)

from __future__ import annotations  # MUST BE FIRST LINE
import uuid
from typing import Optional
from datetime import datetime

from sqlalchemy import String, Text, Boolean, ForeignKey, DateTime  # Import DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infra.persistence.models.sqlalchemy_base import SQLAlchemyBase  # Adjust import path


class TelegramAccountLinkORM(SQLAlchemyBase):
    """
    ORM model for storing Telegram account session links.
    Links an internal BotEntity to a specific Telegram user account session.
    """
    __tablename__ = "telegram_account_links"

    # uid, created_at, updated_at inherited from SQLAlchemyBase

    bot_uid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("bots.uid", ondelete="CASCADE"),
                                               nullable=False, index=True)
    platform_user_uid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                                         ForeignKey("users.uid", ondelete="CASCADE"), nullable=False,
                                                         index=True)

    telegram_user_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, unique=True,
                                                            index=True)  # Telegram's user ID
    phone_number: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)  # Phone used for login
    username: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    session_string: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Encrypted Telethon session string
    phone_code_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Temporary

    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_connected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Optional: Relationship back to BotORM if needed (usually not queried this way)
    # bot: Mapped["BotORM"] = relationship(back_populates="telegram_links")
    # Optional: Relationship back to PlatformUserORM if needed
    # platform_user: Mapped["PlatformUserORM"] = relationship(back_populates="telegram_links")

    def __repr__(self) -> str:
        return f"<TelegramAccountLinkORM bot_uid={self.bot_uid} phone='{self.phone_number}' tg_id='{self.telegram_user_id}' active={self.is_active}>"
