# src/features/bot/api/dtos/update_bot_participant_dto.py (New file or add to existing)

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from pydantic import BaseModel, Field
from uuid import UUID

from src.features.bot.api.v1.dtos.bot_participant import BotParticipantDTO
# Import the Role Enum
from src.features.bot.domain.enums import BotParticipantRole # Adjust import path
# Import Entities if needed for internal DTO
from src.features.bot.domain.entities.bot_entity import BotEntity



# Request DTO (Body of the PATCH request)
class UpdateBotParticipantRoleRequestDTO(BaseModel):
    """Data needed to update a participant's role."""
    # Use the Enum to validate the input role
    role: BotParticipantRole = Field(..., description=f"The new assignable role for the participant. Allowed: {', '.join(BotParticipantRole.list())}")


# Response DTO (Mirrors the structure of BotParticipantResponseItemDTO)
class UpdateBotParticipantRoleResponseDTO(BaseModel):
    """
    Response after successfully updating a participant's role.
    Includes a message and the updated participant details.
    """
    message: str = Field(..., description="A descriptive message about the role update.")
    participant: BotParticipantDTO = Field(..., description="The updated details of the bot participant.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Participant role updated successfully.",
                "participant": {
                    "participant_uid": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                    "bot_uid": "b1c2d3e4-f5a6-7890-1234-abcdef123456",
                    "user_uid": "c1d2e3f4-a5b6-7890-1234-fedcba987654",
                    "email": "participant@example.com",
                    "avatar": "https://example.com/avatars/new_participant.jpg",
                    "role": "admin" # The new role
                }
            }
        }
    }


# Input DTO for the Use Case/Command (internal)
class UpdateBotParticipantRoleInputDTO(BaseModel):
    """Internal DTO carrying necessary data for the update participant role use case."""
    target_bot_entity: BotEntity = Field(..., description="The validated bot entity.")
    participant_user_uid: UUID = Field(..., description="The UID of the user whose role is being updated.")
    new_role: BotParticipantRole = Field(..., description="The validated new role from the request.")
    # current_user: PlatformUserEntity # Optional: Pass user performing the action if needed

    class Config:
        arbitrary_types_allowed = True # Allow BotEntity

