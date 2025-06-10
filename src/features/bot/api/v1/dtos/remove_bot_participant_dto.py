# src/features/bot/api/dtos/remove_bot_participant_dto.py (New file or add to existing)

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

# Import entities if needed for internal DTOs
from src.features.bot.domain.entities.bot_entity import BotEntity
from src.features.identity.domain.entities.user_entity import UserEntity




# No specific request body DTO needed as IDs come from path

# Input DTO for the Use Case/Command (internal)
class UnlinkBotParticipantInputDTO(BaseModel):
    """Internal DTO carrying necessary data for the remove participant use case."""
    target_bot_entity: BotEntity = Field(..., description="The validated bot entity from which to remove the participant.")
    participant_user_uid: UUID = Field(..., description="The UID of the user to remove as a participant.")
    # current_user: PlatformUserEntity # Optional: Pass user performing the action if needed for auditing

    class Config:
        arbitrary_types_allowed = True # Allow BotEntity

# Response DTO
class UnlinkBotParticipantResponseDTO(BaseModel):
    """Response after successfully removing a participant."""
    message: str = "Participant removed successfully."

    model_config = { # Pydantic v2
        "json_schema_extra": {
            "example": {
                "message": "Participant removed successfully."
            }
        }
    }