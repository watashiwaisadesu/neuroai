from abc import ABC, abstractmethod
from uuid import UUID
from src.features.bot.domain.entities.bot_entity import BotEntity


class BotLookupService(ABC):
    @abstractmethod
    async def get_bot(self, bot_uid: UUID) -> BotEntity:
        """Returns bot details by UID, or raises BotNotFoundError."""
        ...