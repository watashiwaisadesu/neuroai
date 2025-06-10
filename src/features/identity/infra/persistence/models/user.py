import uuid
from datetime import date
from typing import List, TYPE_CHECKING

from sqlalchemy import String, Date, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infra.persistence.models.sqlalchemy_base import SQLAlchemyBase

if TYPE_CHECKING:
    # Import BotParticipantORM for type hinting within TYPE_CHECKING
    from src.features.bot.infra.persistence.models.bot_participant import BotParticipantORM
    # Import BotORM if adding back_populates for owned bots
    # from src.features.bot.infra.persistence.models.bot import BotORM

class UserORM(SQLAlchemyBase):
    __tablename__ = "users"

    role: Mapped[str] = mapped_column(String(50), nullable=False, server_default="user")
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=True)
    user_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_send_docs_to_jur_address: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    company_name: Mapped[str] = mapped_column(String(50), nullable=True)
    field_of_activity: Mapped[str] = mapped_column(String(100), nullable=True)
    BIN: Mapped[str] = mapped_column(String(100), nullable=True)
    legal_address: Mapped[str] = mapped_column(String(100), nullable=True)
    contact: Mapped[str] = mapped_column(String(150), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(25), nullable=True)
    registration_date: Mapped[date] = mapped_column(Date, nullable=True, default=None)
    crm_catalog_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avatar_file_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    bot_participations: Mapped[List["BotParticipantORM"]] = relationship(
        "src.features.bot.infra.persistence.models.bot_participant.BotParticipantORM",
        back_populates="user", # Ensure BotParticipantORM.user has this back_populates
        cascade="all, delete-orphan", # If user deleted, remove participations
        lazy="selectin" # Or another loading strategy
    )


    def __repr__(self) -> str:
        return f"<User {self.email}>"
