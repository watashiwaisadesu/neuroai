from pydantic import BaseModel

from src.features.bot.api.v1.dtos.minimal_bot_dto import MinimalBotDTO


class DeleteBotResponseDTO(BaseModel):
    message: str
    bot: MinimalBotDTO

