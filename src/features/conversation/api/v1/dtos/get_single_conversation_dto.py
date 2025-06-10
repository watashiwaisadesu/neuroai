# src/features/conversation/application/queries/get_single_bot_conversation/get_single_bot_conversation.py
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.features.bot.domain.entities.bot_entity import BotEntity


class BotInfoDTO(BaseModel):
    bot_uid: UUID
    bot_name: str

class SenderInfoDTO(BaseModel):
    sender_id: str
    sender_number: Optional[str] = Field(None, description="Sender's phone number, if available.")
    sender_username: Optional[str] = Field(None, description="Sender's username/nickname, if available.")

class OwnerInfoDTO(BaseModel):
    owner_id: UUID

class MessageDTO(BaseModel):
    role: str
    content: str
    timestamp: datetime

class ConversationDTO(BaseModel):
    conversation_uid: UUID
    bot: BotInfoDTO
    sender: SenderInfoDTO
    owner: OwnerInfoDTO
    platform: str
    messages: List[MessageDTO]
    crm_catalog_id: Optional[str]

class GetConversationResponseDTO(BaseModel):
    message: str = Field(..., description="A descriptive message about the retrieved conversation.")
    conversation: ConversationDTO = Field(..., description="Full details of the conversation.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Conversation retrieved successfully.",
                "conversation": {
                    # ... (example of ConversationDTO) ...
                }
            }
        }
    }

