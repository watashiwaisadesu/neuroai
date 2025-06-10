# src/features/bot/api/dtos/get_bot_participants_dto.py (New or existing DTO file)

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from typing import Optional, List # Import List

from src.features.bot.api.v1.dtos.bot_participant import BotParticipantDTO



# DTO for individual participant details in the response list
class BotParticipantResponseItemDTO(BaseModel):
    """DTO representing a participant in a bot, including basic user info."""
    # participant_uid: UUID # UID of the participation record itself (optional to expose)
    user_uid: UUID = Field(..., description="UID of the participant user.")
    email: EmailStr = Field(..., description="Email address of the participant user.")
    avatar: Optional[str] = Field(None, description="URL of the participant user's avatar, if available.")
    role: str = Field(..., description="Role of the participant in the bot.")

    model_config = { # Pydantic v2
        "json_schema_extra": {
            "example": {
                # "participant_uid": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                "user_uid": "c1d2e3f4-a5b6-7890-1234-fedcba987654",
                "email": "participant@example.com",
                "avatar": "https://example.com/avatars/participant.jpg",
                "role": "editor"
            }
        }
    }

class GetParticipantsDTO(BaseModel):
    message: str
    participants: List[BotParticipantDTO]

    participants: List[BotParticipantDTO] = Field(default_factory=list, description="List of bot participants.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Successfully fetched 2 participants for bot.",
                "participants": [
                    {
                        "participant_uid": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                        "bot_uid": "b1c2d3e4-f5a6-7890-1234-abcdef123456",
                        "user_uid": "c1d2e3f4-a5b6-7890-1234-fedcba987654",
                        "email": "owner@example.com",
                        "avatar": "https://example.com/avatars/owner.jpg",
                        "role": "owner"
                    },
                    {
                        "participant_uid": "d1e2f3a4-b5c6-7890-1234-567890abcdef",
                        "bot_uid": "b1c2d3e4-f5a6-7890-1234-abcdef123456",
                        "user_uid": "e1f2a3b4-c5d6-7890-1234-fedcba987654",
                        "email": "collaborator@example.com",
                        "avatar": None,
                        "role": "editor"
                    }
                ]
            }
        }
    }