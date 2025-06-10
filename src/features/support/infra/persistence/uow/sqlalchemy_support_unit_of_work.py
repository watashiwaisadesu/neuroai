# src/features/support/infra/uow/sqlalchemy_support_unit_of_work.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.features.support.domain.uow.support_unit_of_work import SupportUnitOfWork
from src.features.support.infra.persistence.repositories.sqlalchemy_support_repository import SQLAlchemySupportRepository




class SQLAlchemySupportUnitOfWork(SupportUnitOfWork):
    """
    SQLAlchemy implementation of the SupportUnitOfWork.
    Manages session and transaction for support operations.
    """
    def __init__(self, session: AsyncSession, support_repository: SQLAlchemySupportRepository):
        self._session = session
        self.support_repository = support_repository

    async def __aenter__(self):
        self.support_repository = SQLAlchemySupportRepository(self._session)
        logger.debug("SupportUnitOfWork entered. Session and repository initialized.")
        return self # Return self to allow 'as uow' syntax

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type:
                logger.error(f"SupportUnitOfWork exiting with exception: {exc_type.__name__}, rolling back.")
                await self._session.rollback()
            else:
                logger.debug("SupportUnitOfWork exiting normally, committing.")
                await self._session.commit()
        except Exception as e:
            logger.critical(f"Error during SupportUnitOfWork __aexit__ (commit/rollback or close): {e}", exc_info=True)
            raise
        finally:
            if self._session:
                await self._session.close()
                logger.debug("SupportUnitOfWork session closed.")
            self._session = None
            self.support_repository = None

    async def commit(self):
        if self._session:
            logger.debug("SupportUnitOfWork explicit commit.")
            await self._session.commit()
        else:
            logger.warning("Attempted to commit with no active session in SupportUnitOfWork.")

    async def rollback(self):
        if self._session:
            logger.debug("SupportUnitOfWork explicit rollback.")
            await self._session.rollback()
        else:
            logger.warning("Attempted to rollback with no active session in SupportUnitOfWork.")

