from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import String, ForeignKey, DateTime, func, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infra.persistence.models.sqlalchemy_base import SQLAlchemyBase


class BotServiceORM(SQLAlchemyBase):
    __tablename__ = "bot_services"

    bot_uid: Mapped[UUID] = mapped_column(ForeignKey("bots.uid", ondelete="CASCADE"), nullable=False)
    platform: Mapped[str] = mapped_column(String, nullable=False)  # "telegram", "whatsapp", "instagram"
    status: Mapped[str] = mapped_column(String, nullable=False)    # "reserved", "active"
    linked_account_uid: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    service_details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    bot: Mapped["BotORM"] = relationship(
        "BotORM",
        back_populates="bot_services",
        lazy="selectin"
    )