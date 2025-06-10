from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.features.bot.domain.entities.bot_service_entity import BotServiceEntity

class BotServiceRepository(ABC):
    @abstractmethod
    async def create(self, entity: BotServiceEntity) -> BotServiceEntity:
        ...

    @abstractmethod
    async def find_by_uid(self, uid: UUID) -> Optional[BotServiceEntity]:
        ...

    @abstractmethod
    async def find_by_bot_uid(self, bot_uid: UUID) -> List[BotServiceEntity]:
        ...

    async def find_platforms_by_bot_uid(self, bot_uid: UUID) -> list[str]:
        ...

    @abstractmethod
    async def update(self, entity: BotServiceEntity) -> BotServiceEntity:
        ...

    @abstractmethod
    async def find_first_by_bot_platform_status(self, bot_uid: UUID, platform: str, status: str) -> Optional[BotServiceEntity]:
        ...

    @abstractmethod
    async def delete_by_bot_and_platform(self, bot_uid: UUID, platform: str):
        ...