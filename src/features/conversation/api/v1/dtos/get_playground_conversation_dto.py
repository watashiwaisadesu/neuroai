# src/features/conversation/api/dtos/get_playground_conversation.py
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from src.features.bot.domain.entities.bot_entity import BotEntity


# Assuming these DTOs are already defined or can be reused from your
# get_single_conversation example (BotInfoDTO, SenderInfoDTO, OwnerInfoDTO, MessageDTO)
# If not, define them similarly. For this example, I'll assume they exist:

class BotInfoDTO(BaseModel):
    bot_uid: UUID
    bot_name: str

class SenderInfoDTO(BaseModel):
    sender_id: str
    sender_number: str
    sender_username: Optional[str]

class OwnerInfoDTO(BaseModel):
    owner_id: UUID # Or str, based on your UserEntity primary key type

class MessageDTO(BaseModel):
    role: str
    content: str
    timestamp: str # Formatted string

class GetPlaygroundConversationInputDTO(BaseModel):
    bot_uid: UUID
    accessible_bots: List[BotEntity] # Forward reference for BotEntity if not imported yet, or import it
    # current_user_uid: Optional[UUID] = None # If the use case needs direct user context

    class Config:
        arbitrary_types_allowed = True # To allow BotEntity

class PlaygroundConversationDTO(BaseModel):
    conversation_id: UUID
    bot: BotInfoDTO
    sender: SenderInfoDTO
    owner: OwnerInfoDTO
    platform: str = Field(default="playground") # Should always be 'playground'
    messages: List[MessageDTO]
    crm_catalog_id: Optional[str] = None

class GetPlaygroundConversationResponseDTO(BaseModel):
    message: str
    playground_conversations: List[PlaygroundConversationDTO]