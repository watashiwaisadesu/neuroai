from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional # Import Optional


class BotServiceDTO(BaseModel):
    """Represents a service linked to a bot."""
    service_uid: UUID = Field(..., description="The unique ID of the service link record.") # Explicitly named service_uid as the record's UID
    bot_uid: UUID = Field(..., description="UID of the bot this service is linked to.")
    platform: str = Field(..., description="Name of the linked platform (e.g., 'telegram', 'discord').")
    status: str = Field(..., description="Current status of the service link (e.g., 'reserved', 'active', 'error').")
    # You might also include linked_account_uid or relevant service_details if they are public
    linked_account_uid: Optional[UUID] = Field(None, description="UID of the linked external account, if applicable.")


    model_config = { # Pydantic v2
        "json_schema_extra": {
            "example": {
                "service_uid": "e1f2a3b4-c5d6-7890-1234-fedcba987654",
                "bot_uid": "b1c2d3e4-f5a6-7890-1234-abcdef123456",
                "platform": "telegram",
                "status": "active",
                "linked_account_uid": "f1e2d3c4-b5a6-7890-1234-abcdef123456"
            }
        }
    }