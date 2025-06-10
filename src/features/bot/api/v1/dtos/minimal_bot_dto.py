# src/features/identity/api/dtos/bot_dtos.py (continued)
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Literal

class MinimalBotDTO(BaseModel):
    """
    Represents a minimal Data Transfer Object for a 'Bot'.
    Intended for quick identification and status checks.
    """
    uid: UUID = Field(..., description="Unique identifier of the bot itself.")
    user_uid: UUID = Field(..., description="The unique identifier of the human user that owns or controls this bot.")
    name: str = Field(..., description="The name of the bot.")
    status: Literal["draft","active", "inactive", "suspended", "error"] = Field(..., description="Current operational status of the bot.")

    class Config:
        from_attributes = True