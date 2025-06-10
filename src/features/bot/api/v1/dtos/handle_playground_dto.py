# src/features/bot/api/dtos/playground_dto.py (New file or add to existing bot DTOs)

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from pydantic import BaseModel, Field
from typing import Any # Import Any for WebSocket

# Import entities needed for the internal DTO
from src.features.bot.domain.entities.bot_entity import BotEntity
from src.features.identity.domain.entities.user_entity import UserEntity



# Input DTO for the Use Case/Command (Internal)
class HandlePlaygroundConnectionInputDTO(BaseModel):
    """Internal DTO carrying necessary data for the playground connection handler."""
    websocket: Any # FastAPI's WebSocket type
    target_bot_entity: BotEntity = Field(..., description="The validated BotEntity for the playground session.")
    current_user: UserEntity = Field(..., description="The authenticated user initiating the session.")
    # No specific request body DTO from client for websocket messages, they are text.

    class Config:
        arbitrary_types_allowed = True # Allow WebSocket, BotEntity, PlatformUserEntity


