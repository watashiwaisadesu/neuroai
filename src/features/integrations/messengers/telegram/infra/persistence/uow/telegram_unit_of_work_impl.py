# src/features/integrations/telegram/infra/uow/telegram_unit_of_work_impl.py (New file)

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from sqlalchemy.ext.asyncio import AsyncSession

# Import interfaces and concrete repository implementation
from src.features.integrations.messengers.telegram.domain.uow.telegram_unit_of_work import TelegramUnitOfWork
from src.features.integrations.messengers.telegram.domain.repositories.telegram_account_link_repository import TelegramAccountLinkRepository
from src.features.integrations.messengers.telegram.infra.persistence.repositories.telegram_account_link_repository_impl import SQLAlchemyTelegramAccountLinkRepository



class SQLAlchemyTelegramUnitOfWork(TelegramUnitOfWork):
    """Concrete implementation of the Unit of Work for Telegram Integration using SQLAlchemy."""

    _session: AsyncSession
    # Use interface type hint for repositories
    account_link_repository: TelegramAccountLinkRepository
    # Add other Telegram-specific repositories here if needed

    def __init__(self, session: AsyncSession):
        self._session = session
        # Instantiate the concrete repository with the session
        self.account_link_repository = SQLAlchemyTelegramAccountLinkRepository(session)
        # Instantiate other repositories
        logger.debug("TelegramUnitOfWorkImpl initialized.")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()
        await self._session.close()

    async def begin(self) -> None:
        await self._session.begin()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()