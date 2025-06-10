# src/features/announcements/domain/repositories/announcement_repository.py

import uuid
from abc import ABC, abstractmethod
from typing import List, Optional

from src.features.announcement.domain.entities.announcement_entity import AnnouncementEntity


class AnnouncementRepository(ABC):
    """
    Abstract Base Class for Announcement Repository.
    Defines the contract for interacting with announcement persistence.
    """
    @abstractmethod
    async def create(self, announcement: AnnouncementEntity) -> AnnouncementEntity:
        """Adds a new announcement to the repository."""
        pass

    @abstractmethod
    async def get_by_uid(self, uid: uuid.UUID) -> Optional[AnnouncementEntity]:
        """Retrieves an announcement by its unique identifier."""
        pass

    @abstractmethod
    async def get_all(self) -> List[AnnouncementEntity]:
        """Retrieves all announcements."""
        pass

    @abstractmethod
    async def update(self, announcement: AnnouncementEntity) -> AnnouncementEntity:
        """Updates an existing announcement."""
        pass

    @abstractmethod
    async def delete(self, uid: uuid.UUID) -> None:
        """Deletes an announcement by its unique identifier."""
        pass