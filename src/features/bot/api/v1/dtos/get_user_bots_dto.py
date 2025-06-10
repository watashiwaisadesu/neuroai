# src/features/bot/api/dtos/get_user_bots_dto.py

from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, UUID4, Field, EmailStr

from src.features.bot.api.v1.dtos.get_documents_dto import BotDocumentResponseItemDTO
from src.features.bot.api.v1.dtos.minimal_bot_dto import MinimalBotDTO


class BotServiceDTO(BaseModel):
    uid: UUID4
    platform: str
    status: str
    service_details: Optional[Dict[str, Any]] = None,

class BotParticipantDTO(BaseModel):
    """DTO representing a participant in a bot, including basic user info."""
    # participant_uid: UUID # UID of the participation record itself (optional to expose)
    user_uid: UUID = Field(..., description="UID of the participant user.")
    email: EmailStr = Field(..., description="Email address of the participant user.") # Added
    avatar: Optional[str] = Field(None, description="URL of the participant user's avatar, if available.") # Added
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


class BotDTO(BaseModel):
    uid: UUID4
    user_uid: UUID4
    bot_type: str
    name: str
    instructions: str
    temperature: float
    token_limit: int
    tokens_left: int
    auto_deduction: bool
    status: str
    tariff: str
    crm_lead_id: int
    max_response: int
    top_p: float
    top_k: int
    repetition_penalty: float
    generation_model: str
    crm_lead_id: Optional[int]

    bot_services: List[BotServiceDTO]
    participants: List[BotParticipantDTO] = Field(default_factory=list,
                                                  description="List of users participating in this bot.")
    documents: List[BotDocumentResponseItemDTO] = Field(default_factory=list,
                                                        description="List of documents associated with this bot.")


class BotResponseDTO(BaseModel):
    message: str
    bot: BotDTO

class GetUserBotsResponse(BaseModel):
    message: str
    bots: List[BotDTO] = Field(default_factory=list, description="List of bots accessible by the user.")

class GetLastActiveBotsResponse(BaseModel):
    """
    API response DTO for the last active bots query.
    Includes a message and a list of minimal bot details.
    """
    message: str = Field(..., description="A descriptive message about the retrieval of bots.")
    bots: List[MinimalBotDTO] = Field(default_factory=list, description="List of minimal bot details accessible by the user, sorted by last activity.")
