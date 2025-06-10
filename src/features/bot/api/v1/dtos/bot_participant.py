from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from uuid import UUID

from src.features.bot.domain.entities.bot_entity import BotEntity
from src.features.bot.domain.enums import BotParticipantRole




class BotParticipantDTO(BaseModel):
    """Response after successfully adding a participant."""
    participant_uid: UUID = Field(..., description="The unique ID of the newly created participant record.") # Using the participant record's own UID
    bot_uid: UUID = Field(..., description="The UID of the bot.")
    user_uid: UUID = Field(..., description="The UID of the user added as a participant.")
    email: Optional[str] = Field(None,
                                 description="Email address of the participant user (optional, if fetched).")  # Keep optional
    avatar: Optional[str] = Field(None,
                                  description="URL of the participant user's avatar (optional, if fetched).")  # Keep optional
    role: str = Field(..., description="The assigned role.")
    # avatar: Optional[str] = None # Avoid returning avatar here; fetch user details separately if needed

    model_config = { # Pydantic v2 uses model_config
        "json_schema_extra": {
            "example": {
                "participant_uid": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                "bot_uid": "b1c2d3e4-f5a6-7890-1234-abcdef123456",
                "user_uid": "c1d2e3f4-a5b6-7890-1234-fedcba987654",
                "email": "participant@example.com",
                "role": "editor"
            }
        }
    }