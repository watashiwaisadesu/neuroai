# src/features/integrations/telegram/domain/repositories/telegram_account_link_repository.py

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.features.integrations.messengers.telegram.domain.entities.telegram_account_link_entity import TelegramAccountLinkEntity
from src.core.base.repository import BaseRepository # Adjust import path

class TelegramAccountLinkRepository(BaseRepository[TelegramAccountLinkEntity]):
    """
    Abstract interface for Telegram Account Link data access.
    An "Account Link" represents a specific Telegram user account
    session linked to one of our internal bots.
    """

    async def find_by_uid(self, uid: UUID) -> Optional[TelegramAccountLinkEntity]:
        raise NotImplementedError

    @abstractmethod
    async def find_by_phone_number(self, phone_number: str) -> Optional[TelegramAccountLinkEntity]:
        """Finds a Telegram account link by phone number."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_telegram_user_id(self, telegram_user_id: str) -> Optional[TelegramAccountLinkEntity]:
        """Finds a Telegram account link by the Telegram User ID."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_bot_uid(self, bot_uid: UUID) -> Optional[TelegramAccountLinkEntity]:
        """Finds the Telegram account link associated with a specific internal bot UID."""
        # Assuming one bot links to one Telegram account for listening.
        # If a bot can link multiple, this would return List[...].
        raise NotImplementedError

    @abstractmethod
    async def find_all_active_sessions(self) -> List[TelegramAccountLinkEntity]:
        """Finds all account links with active sessions, for session resumption."""
        raise NotImplementedError

    # create, update, delete_by_uid, find_by_uid are inherited from BaseRepository
