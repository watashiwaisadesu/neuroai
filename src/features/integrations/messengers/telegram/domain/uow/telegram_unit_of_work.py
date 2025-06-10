# src/features/integrations/telegram/domain/uow/telegram_unit_of_work.py (New file)

from abc import ABC, abstractmethod

# Import repository interface
from src.features.integrations.messengers.telegram.domain.repositories.telegram_account_link_repository import TelegramAccountLinkRepository
from src.core.base.unit_of_work import BaseUnitOfWork # Adjust import path

class TelegramUnitOfWork(BaseUnitOfWork[TelegramAccountLinkRepository]):
    """
    Unit of Work interface for the Telegram Integration feature.
    """
    account_link_repository: TelegramAccountLinkRepository # Specific name

    # Add other Telegram-specific repositories here if needed in the future

    @abstractmethod
    async def __aenter__(self):
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    @abstractmethod
    async def commit(self):
        raise NotImplementedError

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError
