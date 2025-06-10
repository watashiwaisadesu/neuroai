# src/features/support/domain/uow/support_unit_of_work.py

from abc import ABC, abstractmethod

from src.features.support.domain.repossitories.support_repository import SupportRepository


class SupportUnitOfWork(ABC):
    """
    Abstract Base Class for the Support Request Unit of Work.
    Manages transactional operations for support requests.
    """
    support_repository: SupportRepository

    @abstractmethod
    async def __aenter__(self):
        """Enter the asynchronous context manager."""
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the asynchronous context manager, handling commit/rollback."""
        pass

    @abstractmethod
    async def commit(self):
        """Commits the current transaction."""
        pass

    @abstractmethod
    async def rollback(self):
        """Rolls back the current transaction."""
        pass