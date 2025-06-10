from pydantic import BaseModel, Field

from src.features.bot.domain.entities.bot_entity import BotEntity
from src.features.identity.domain.entities.user_entity import UserEntity


class DuplicateBotInputDTO(BaseModel):
    """
    Input data required by the DuplicateBotCommand use case.
    Passed from the API layer after access checks.
    """
    original_bot_entity: BotEntity = Field(..., description="The validated BotEntity object to duplicate.")
    owner_user: UserEntity = Field(..., description="The user who will own the new duplicated bot.")

    # Allow arbitrary types for Pydantic to handle custom classes like BotEntity
    class Config:
        arbitrary_types_allowed = True


