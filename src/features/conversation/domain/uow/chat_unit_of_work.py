# src/features/chat/domain/repositories/chat_unit_of_work.py (New file)

from abc import ABC, abstractmethod
from typing import TypeVar

# Import repository interface
from src.features.conversation.domain.repositories.conversation_repository import IConversationRepository
# Import base UoW if inheriting
from src.core.base.unit_of_work import BaseUnitOfWork # Adjust import path
from src.features.conversation.domain.repositories.message_repository import IMessageRepository

# Define type variable if BaseUnitOfWork is generic
RepoType = TypeVar("RepoType")

# If BaseUnitOfWork is generic like BaseUnitOfWork[RepoType]
class ConversationUnitOfWork(BaseUnitOfWork[IConversationRepository]):
    """
    Unit of Work interface for the Chat bounded context.
    Provides access to the Conversation repository.
    """
    # The primary repository for the aggregate root
    conversation_repository: IConversationRepository # Use IConversationRepository type hint
    message_repository: IMessageRepository

    # Add other chat-related repositories here if needed in the future
    # message_repository: IMessageRepository

    # --- Async Context Manager Methods (essential for 'async with') ---
    @abstractmethod
    async def __aenter__(self):
        """Enter the async runtime context."""
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async runtime context, handling commit or rollback."""
        raise NotImplementedError

    @abstractmethod
    def begin(self) -> None:
        raise NotImplementedError()

    # --- Optional Explicit Transaction Control Methods ---
    @abstractmethod
    async def commit(self):
        """Commit the current transaction."""
        raise NotImplementedError

    @abstractmethod
    async def rollback(self):
        """Rollback the current transaction."""
        raise NotImplementedError

