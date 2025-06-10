from src.infra.logging.setup_async_logging import async_logger
logger = async_logger

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Import Command Interfaces and Implementations
# get_telegram_unit_of_work assumed to be defined in this file
# from .uow.telegram_unit_of_work_impl import TelegramUnitOfWorkImpl # For get_telegram_unit_of_work
from src.features.integrations.messengers.telegram.domain.repositories.telegram_account_link_repository import \
    TelegramAccountLinkRepository
# Import UoW provider, service providers
from src.features.integrations.messengers.telegram.domain.uow.telegram_unit_of_work import TelegramUnitOfWork
from src.features.integrations.messengers.telegram.infra.persistence.repositories.telegram_account_link_repository_impl import \
    SQLAlchemyTelegramAccountLinkRepository
from src.features.integrations.messengers.telegram.infra.persistence.uow.telegram_unit_of_work_impl import SQLAlchemyTelegramUnitOfWork
from src.infra.persistence.connection.sqlalchemy_engine import get_async_db




async def get_telegram_account_link_repository(
    session: AsyncSession
) -> TelegramAccountLinkRepository:
    """Provides an instance of the TelegramAccountLinkRepository."""
    logger.debug("Providing TelegramAccountLinkRepositoryImpl")
    return SQLAlchemyTelegramAccountLinkRepository(session=session)

# --- Telegram UoW Provider ---
async def get_telegram_unit_of_work(
    session: AsyncSession = Depends(get_async_db),
    # account_link_repo: ITelegramAccountLinkRepository = Depends(get_telegram_account_link_repository) # Alternative: inject repo
) -> TelegramUnitOfWork:
    """Provides an instance of the Telegram Unit of Work."""
    logger.debug("Providing TelegramUnitOfWorkImpl")
    # TelegramUnitOfWorkImpl instantiates its own repositories using the session
    return SQLAlchemyTelegramUnitOfWork(session=session)

