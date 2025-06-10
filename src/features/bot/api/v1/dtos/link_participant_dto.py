from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from pydantic import BaseModel, EmailStr, Field

from src.features.bot.api.v1.dtos.bot_participant import BotParticipantDTO
from src.features.bot.domain.enums import BotParticipantRole



class LinkBotParticipantRequestDTO(BaseModel):
    """Data needed to add a participant."""
    email: EmailStr = Field(..., description="Email address of the user to add as a participant.")
    role: BotParticipantRole = Field(..., description=f"Role to assign to the participant. Allowed roles: {', '.join(BotParticipantRole.list())}")

    model_config = { # Pydantic v2
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "role": "editor" # Example uses a valid Enum value
            }
        }
    }

#
# class LinkBotParticipantDTO(BaseModel):
#     """Response after successfully adding a participant."""
#     participant_uid: UUID = Field(..., description="The unique ID of the newly created participant record.") # Using the participant record's own UID
#     bot_uid: UUID = Field(..., description="The UID of the bot.")
#     user_uid: UUID = Field(..., description="The UID of the user added as a participant.")
#     email: EmailStr = Field(..., description="The email of the added participant (for confirmation).")
#     role: str = Field(..., description="The assigned role.")
#     # avatar: Optional[str] = None # Avoid returning avatar here; fetch user details separately if needed
#
#     model_config = { # Pydantic v2 uses model_config
#         "json_schema_extra": {
#             "example": {
#                 "participant_uid": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
#                 "bot_uid": "b1c2d3e4-f5a6-7890-1234-abcdef123456",
#                 "user_uid": "c1d2e3f4-a5b6-7890-1234-fedcba987654",
#                 "email": "participant@example.com",
#                 "role": "editor"
#             }
#         }
#     }

class LinkBotParticipantResponseDTO(BaseModel):
    message: str
    participant: BotParticipantDTO
