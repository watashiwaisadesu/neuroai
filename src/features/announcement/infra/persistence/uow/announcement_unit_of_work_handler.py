from sqlalchemy.ext.asyncio import AsyncSession

from src.features.announcement.domain.repositories.announcement_repository import AnnouncementRepository
from src.features.announcement.domain.uow.announcement_unit_of_work import AnnouncementUnitOfWork
from src.features.announcement.infra.persistence.repositories.announcement_repository_handler import AnnouncementRepositoryHandler


class AnnouncementUnitOfWorkHandler(AnnouncementUnitOfWork):
    """
    SQLAlchemy implementation of the AnnouncementUnitOfWork.
    Manages a single session and transaction for all repositories within this UoW.
    """
    def __init__(self, session: AsyncSession, announcement_repository: AnnouncementRepositoryHandler):
        self._session = session
        self.announcement_repository = announcement_repository

    async def __aenter__(self):
        """Begins a new transaction on entering the context."""
        await self._session.begin()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Commits or rolls back the transaction on exiting the context."""
        if exc_type is None:
            await self._session.commit()
        else:
            await self._session.rollback()
        await self._session.close() # Ensure session is closed after use

    async def commit(self):
        """Commits the current transaction."""
        await self._session.commit()

    async def rollback(self):
        """Rolls back the current transaction."""
        await self._session.rollback()
