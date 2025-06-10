from abc import abstractmethod
from typing import List
from uuid import UUID

from src.core.base.repository import BaseRepository
from src.features.bot.domain.entities.bot_entity import BotEntity


class BotRepository(BaseRepository[BotEntity]):

    # in BotRepository
    @abstractmethod
    async def findall_by_user_uid(self, user_uid: UUID) -> List[BotEntity]:
        ...

    @abstractmethod
    async def find_by_uids(self, uids: List[UUID]) -> List[BotEntity]:
        """Finds multiple bots by their UIDs."""
        raise NotImplementedError
