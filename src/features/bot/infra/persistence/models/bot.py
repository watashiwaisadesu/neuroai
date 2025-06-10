from __future__ import annotations
import uuid
from typing import List, TYPE_CHECKING

from sqlalchemy import String, Text, Float, ForeignKey, Integer, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


from src.infra.persistence.models.sqlalchemy_base import SQLAlchemyBase

if TYPE_CHECKING:
    from src.features.payments.infra.persistence.models.payment import PaymentORM
    from src.features.bot.infra.persistence.models.bot_service import BotServiceORM
    # Import BotParticipantORM for type hinting within TYPE_CHECKING
    from src.features.bot.infra.persistence.models.bot_participant import BotParticipantORM
    from src.features.bot.infra.persistence.models.bot_document import BotDocumentORM


class BotORM(SQLAlchemyBase):
    __tablename__ = "bots"

    user_uid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.uid", ondelete="CASCADE"),
        nullable=False
    )
    bot_type: Mapped[str] = mapped_column(String, nullable=False)

    name: Mapped[str | None] = mapped_column(String, nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)

    temperature: Mapped[float | None] = mapped_column(Float, default=0.5, nullable=True)
    status: Mapped[str] = mapped_column(String, default="draft", nullable=False)

    tariff: Mapped[str | None] = mapped_column(String, default="No tariff", nullable=True)
    auto_deduction: Mapped[bool | None] = mapped_column(Boolean, default=False, nullable=True)

    max_response: Mapped[int | None] = mapped_column(Integer, default=250, nullable=True)
    top_p: Mapped[float | None] = mapped_column(Float, default=0.9, nullable=True)
    top_k: Mapped[int | None] = mapped_column(Integer, default=40, nullable=True)
    repetition_penalty: Mapped[float | None] = mapped_column(Float, default=0.0, nullable=True)
    generation_model: Mapped[str] = mapped_column(String, default="stub", nullable=False)

    token_limit: Mapped[int | None] = mapped_column(Integer, default=500, nullable=True)
    tokens_left: Mapped[int | None] = mapped_column(Integer, default=50000, nullable=True)

    crm_lead_id: Mapped[int | None] = mapped_column(Integer, nullable=True)


    payments: Mapped[List["PaymentORM"]] = relationship(
        "src.features.payments.infra.persistence.models.payment.PaymentORM",
        back_populates="bot",
        cascade="all, delete-orphan",
        lazy="selectin",
        passive_deletes=True
    )

    bot_services: Mapped[List["BotServiceORM"]] = relationship(
        "BotServiceORM",
        back_populates="bot",
        cascade="all, delete-orphan",
        lazy="selectin",
        passive_deletes=True
    )

    bot_participants: Mapped[List["BotParticipantORM"]] = relationship(
        "src.features.bot.infra.persistence.models.bot_participant.BotParticipantORM",
        back_populates="bot",  # Matches BotParticipantORM.bot relationship
        cascade="all, delete-orphan",
        lazy="selectin",
        passive_deletes=True
    )

    documents: Mapped[List["BotDocumentORM"]] = relationship(
        "src.features.bot.infra.persistence.models.bot_document.BotDocumentORM",
        back_populates="bot", # This should match the 'bot' relationship in BotDocumentORM
        cascade="all, delete-orphan",
        lazy="selectin" # Or your preferred loading strategy
    )

