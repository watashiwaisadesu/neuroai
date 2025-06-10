
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.features.prices.domain.entities.price_entity import PlatformPriceEntity


class PlatformPriceRepository(ABC):
    """Abstract interface for managing PlatformPriceEntity objects."""

    @abstractmethod
    async def add(self, entity: PlatformPriceEntity) -> None:
        pass

    @abstractmethod
    async def get_by_service_name(self, service_name: str) -> Optional[PlatformPriceEntity]:
        pass

    @abstractmethod
    async def get_all(self) -> List[PlatformPriceEntity]:
        pass

    @abstractmethod
    async def update(self, entity: PlatformPriceEntity) -> None:
        pass

    @abstractmethod
    async def delete(self, uid: UUID) -> None:
        pass