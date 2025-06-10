import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

# Ensure this import path is correct for your TelegramAccountLinkEntity
from src.features.integrations.messengers.telegram.domain.entities.telegram_account_link_entity import \
    TelegramAccountLinkEntity


class ReassignTelegramLinkRequestDTO(BaseModel):
    new_bot_uid: uuid.UUID


class TelegramAccountLinkResponseDTO(BaseModel):
    """
    Represents a Telegram Account Link for API responses.
    Excludes sensitive data like session strings and phone code hashes.
    """
    uid: uuid.UUID = Field(..., description="Unique identifier of the Telegram account link.")
    bot_uid: uuid.UUID = Field(..., description="The unique ID of the bot this Telegram account is linked to.")
    platform_user_uid: uuid.UUID = Field(..., description="The unique ID of the user who linked this Telegram account.")
    phone_number: str = Field(..., description="The phone number associated with the Telegram account.")
    telegram_user_id: Optional[str] = Field(None, description="The unique user ID from Telegram, if available.")
    username: Optional[str] = Field(None, description="The Telegram username, if available.")
    is_active: bool = Field(..., description="Indicates if the Telegram link/session is currently active.")
    last_connected_at: Optional[datetime] = Field(None, description="The timestamp of the last successful connection to Telegram.")
    created_at: datetime = Field(..., description="Timestamp when the link was created.")
    updated_at: datetime = Field(..., description="Timestamp when the link was last updated.")

    class Config:
        # Allows Pydantic to read attributes directly from ORM models (like your entity)
        from_attributes = True

    @staticmethod
    def from_entity(entity: TelegramAccountLinkEntity) -> "TelegramAccountLinkResponseDTO":
        """
        Converts a TelegramAccountLinkEntity domain entity into a TelegramAccountLinkResponseDTO.
        This ensures only safe, relevant data is exposed.
        """
        return TelegramAccountLinkResponseDTO(
            uid=entity.uid,
            bot_uid=entity.bot_uid,
            platform_user_uid=entity.platform_user_uid,
            phone_number=entity.phone_number,
            telegram_user_id=entity.telegram_user_id,
            username=entity.username,
            is_active=entity.is_active,
            last_connected_at=entity.last_connected_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )