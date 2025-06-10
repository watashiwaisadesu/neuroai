# src/features/integrations/telegram/api/dtos/telegram_auth_dtos.py (New file)

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from uuid import UUID

from pydantic import BaseModel, Field

from src.features.bot.domain.entities.bot_entity import BotEntity  # For internal DTO
from src.features.identity.domain.entities.user_entity import UserEntity  # For internal DTO



# --- Request DTOs ---
class TelegramPhoneNumberRequestDTO(BaseModel):
    phone_number: str = Field(..., description="The phone number to link with Telegram.")

class TelegramVerificationCodeRequestDTO(BaseModel):
    phone_number: str = Field(..., description="The phone number associated with the code.")
    code: str = Field(..., description="The verification code received by the user.")

# --- Response DTOs ---
class RequestTelegramCodeResponseDTO(BaseModel):
    status: str = "Code sent"
    phone_code_hash: str
    # We might also return the temporary session string for client-side state if needed,
    # but better to manage state server-side or via secure cookies if possible.
    # For now, assume server handles temporary session.

class SubmitTelegramCodeResponseDTO(BaseModel):
    status: str = "Logged in successfully to Telegram"
    telegram_user_id: str
    bot_uid: UUID
    # Optionally include parts of the updated bot DTO if needed
    # bot_services: List[str] = Field(default_factory=list)

# --- Internal Input DTOs for Commands ---
class RequestTelegramCodeInputDTO(BaseModel):
    """Internal DTO for RequestTelegramCodeCommand."""
    target_bot_entity: BotEntity
    current_user: UserEntity # User performing the action
    phone_number: str

    class Config:
        arbitrary_types_allowed = True

class SubmitTelegramCodeInputDTO(BaseModel):
    """Internal DTO for SubmitTelegramCodeCommand."""
    target_bot_entity: BotEntity
    current_user: UserEntity # User performing the action
    phone_number: str
    code: str

    class Config:
        arbitrary_types_allowed = True


