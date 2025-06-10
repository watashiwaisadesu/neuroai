# src/features/chat/api/dtos/get_all_conversations_dto.py (New file)

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List
from datetime import datetime # Import datetime



# --- Nested DTOs for structure ---

class LastMessageItemDTO(BaseModel):
    """Represents the content and timestamp of the last message."""
    content: str
    timestamp: datetime # Use datetime for consistency, format in frontend if needed

class BotInfoDTO(BaseModel):
    """Basic info about the bot associated with the conversation."""
    bot_uid: UUID
    bot_name: Optional[str] = None

class SenderInfoDTO(BaseModel):
    """Basic info about the external sender in the conversation."""
    sender_id: str # External platform ID
    sender_number: Optional[str] = None
    sender_username: Optional[str] = None # Changed from sender_nickname

class OwnerInfoDTO(BaseModel):
    """Basic info about the owner of the conversation (your platform user)."""
    owner_uid: UUID # Changed from owner_id to match entity

# --- Main Response DTO per Conversation ---

class ConversationMinimalDTO(BaseModel):
    """Minimal details of a conversation, including the last message."""
    conversation_uid: UUID = Field(..., description="Internal unique ID of the conversation.")
    # conversation_id: Optional[str] = None # Optional: Original external ID if kept
    platform: str = Field(..., description="Platform the conversation occurred on (e.g., telegram, playground).")
    bot: BotInfoDTO = Field(..., description="Information about the associated bot.")
    sender: SenderInfoDTO = Field(..., description="Information about the external sender.")
    owner: OwnerInfoDTO = Field(..., description="Information about the conversation owner (platform user).")
    last_message: Optional[LastMessageItemDTO] = Field(None, description="The last message exchanged in the conversation.")
    crm_catalog_id: Optional[int] = Field(None, description="Associated CRM Catalog ID, if any.")
    updated_at: Optional[datetime] = Field(None, description="Timestamp of the last update to the conversation.") # Useful for sorting

    model_config = { # Pydantic v2
        "json_schema_extra": {
            "example": {
                "conversation_uid": "d1e2f3a4-b5c6-7890-1234-abcdef123456",
                "platform": "playground",
                "bot": {
                    "bot_uid": "b1c2d3e4-f5a6-7890-1234-abcdef123456",
                    "bot_name": "Sales Bot Alpha"
                },
                "sender": {
                    "sender_id": "user_playground_123",
                    "sender_number": None,
                    "sender_username": "PlaygroundUser"
                },
                "owner": {
                    "owner_uid": "c1d2e3f4-a5b6-7890-1234-fedcba987654"
                },
                "last_message": {
                    "content": "Okay, thank you!",
                    "timestamp": "2025-05-06T14:30:00Z"
                },
                "crm_catalog_id": 54321,
                 "updated_at": "2025-05-06T14:30:00Z"
            }
        }
    }


class GetConversationsResponseDTO(BaseModel):
    message: str
    conversations: List[ConversationMinimalDTO]