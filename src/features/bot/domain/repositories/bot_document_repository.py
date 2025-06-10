# src/features/bot/domain/repositories/bot_document_repository.py

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.features.bot.domain.entities.bot_document_entity import BotDocumentEntity
from src.core.base.repository import BaseRepository  # Assuming you have this


class BotDocumentRepository(ABC):  # Inherit if applicable
    """Abstract interface for Bot Document data access."""

    @abstractmethod
    async def create(self, entity: BotDocumentEntity) -> BotDocumentEntity:
        raise NotImplementedError

    @abstractmethod
    async def create_many(self, entities: List[BotDocumentEntity]) -> List[BotDocumentEntity]:
        """Persists multiple document entities."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_bot_uid(self, bot_uid: UUID) -> List[BotDocumentEntity]:
        """Finds all documents associated with a specific bot."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_uid(self, uid: UUID) -> Optional[BotDocumentEntity]:
        raise NotImplementedError

    @abstractmethod
    async def delete_by_uid(self, uid: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def find_by_uids_and_bot_uid(self, document_uids: List[UUID], bot_uid: UUID) -> List[BotDocumentEntity]:
        """Finds documents by their UIDs, ensuring they belong to the specified bot."""
        raise NotImplementedError

    @abstractmethod
    async def delete_by_uids(self, uids: List[UUID]) -> int:
        """Deletes multiple documents by their UIDs. Returns the count of deleted documents."""
        raise NotImplementedError

    # Add update if needed, though documents are often immutable once uploaded
    # @abstractmethod
    # async def update(self, entity: BotDocumentEntity) -> BotDocumentEntity:
    #     raise NotImplementedError
