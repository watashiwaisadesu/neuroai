from src.infra.logging.setup_async_logging import async_logger
logger = async_logger

from pydantic import BaseModel, EmailStr, Field
from src.features.bot.domain.entities.bot_entity import BotEntity



class TransferBotRequestDTO(BaseModel):
    """Request body for transferring bot ownership."""
    new_owner_email: EmailStr = Field(..., description="Email address of the user to transfer the bot to.")

# Response DTO can reuse BotResponseDTO if it returns the updated bot details
# from src.features.bot.api.dtos.get_user_bots_dto import BotResponseDTO # Already exists

# Internal Input DTO for the Use Case/Command
class TransferBotInputDTO(BaseModel):
    """Internal DTO carrying necessary data for the TransferBotCommand use case."""
    target_bot_entity: BotEntity = Field(..., description="The validated BotEntity object to be transferred.")
    new_owner_email: EmailStr = Field(..., description="Email of the new owner.")
    # current_user_performing_transfer: PlatformUserEntity # The user initiating the transfer

    class Config:
        arbitrary_types_allowed = True