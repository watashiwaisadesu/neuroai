# src/features/support/domain/repositories/support_repository.py

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from src.features.support.domain.entities.support_entity import SupportEntity
from src.features.support.domain.value_objects.support_enums import SupportCategory


class SupportRepository(ABC):
    """
    Abstract Base Class for the Support Request Repository.
    Defines the contract for persisting and retrieving support request entities.
    """
    @abstractmethod
    async def create(self, entity: SupportEntity) -> SupportEntity:
        """Adds a new support request to the repository."""
        pass

    @abstractmethod
    async def get_by_uid(self, uid: UUID) -> Optional[SupportEntity]:
        """Retrieves a support request by its unique identifier."""
        pass

    @abstractmethod
    async def update(self, entity: SupportEntity) -> SupportEntity:
        """Updates an existing support request in the repository."""
        pass

    @abstractmethod
    async def delete_by_uid(self, uid: UUID) -> None:
        """Deletes a support request by its unique identifier."""
        pass

    @abstractmethod
    async def get_all_by_user_uid(self, user_uid: UUID, category: Optional[SupportCategory] = None) -> List[
        SupportEntity]:
        """Retrieves all support requests for a specific user."""
        pass

    @abstractmethod
    async def get_all(self) -> List[SupportEntity]:
        """Retrieves all support requests (e.g., for admin dashboard)."""
        pass