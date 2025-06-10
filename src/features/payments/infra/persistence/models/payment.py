from __future__ import annotations
from datetime import datetime
import uuid

from sqlalchemy import String, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infra.persistence.models.sqlalchemy_base import SQLAlchemyBase


class PaymentORM(SQLAlchemyBase):
    __tablename__ = "payments"

    bot_uid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bots.uid", ondelete="CASCADE"),
        nullable=False
    )

    user_uid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.uid", ondelete="CASCADE"),
        nullable=False
    )

    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String, default="pending", nullable=False)  # success, failed, pending
    payment_method: Mapped[str] = mapped_column(String, nullable=False)
    transaction_uid: Mapped[str] = mapped_column(String, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    bot: Mapped["BotORM"] = relationship(
         "src.features.bot.infra.persistence.models.bot.BotORM",
        back_populates="payments",
        lazy="selectin"
    )
