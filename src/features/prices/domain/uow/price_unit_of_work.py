from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.features.prices.domain.entities.price_entity import PlatformPriceEntity
from src.features.prices.domain.repositories.price_repository import PlatformPriceRepository


class PriceUnitOfWork(ABC):
    """Abstract interface for a Unit of Work for price-related operations."""

    platform_price_repository: PlatformPriceRepository

    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    async def commit(self):
        pass

    @abstractmethod
    async def rollback(self):
        pass