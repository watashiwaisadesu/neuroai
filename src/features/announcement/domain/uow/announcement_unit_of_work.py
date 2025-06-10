from abc import ABC, abstractmethod

from src.features.announcement.domain.repositories.announcement_repository import AnnouncementRepository


class AnnouncementUnitOfWork(ABC):
    """
    Abstract Base Class for Announcement Unit of Work.
    Defines the contract for managing database operations for announcements.
    """
    announcement_repository: AnnouncementRepository

    @abstractmethod
    async def __aenter__(self):
        """Enter the async context, typically starting a transaction."""
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context, committing or rolling back the transaction."""
        pass

    @abstractmethod
    async def commit(self):
        """Explicitly commit the current transaction."""
        pass

    @abstractmethod
    async def rollback(self):
        """Explicitly rollback the current transaction."""
        pass