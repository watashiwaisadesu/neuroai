# src/features/chat/domain/repositories/conversation_repository.py

from abc import abstractmethod
from typing import List, Optional
from uuid import UUID

# Import domain entity and related types
from src.features.conversation.domain.entities.conversation_entity import ConversationEntity
# Import BaseRepository if inheriting
from src.core.base.repository import BaseRepository # Adjust import path
from src.features.conversation.domain.enums import ChatPlatform


# Inherit from BaseRepository, specifying the Entity type
class IConversationRepository(BaseRepository[ConversationEntity]):
    """
    Abstract interface for Conversation data access.
    Inherits basic CRUD from BaseRepository and adds specific query methods.
    """

    # --- Methods from BaseRepository (Must be implemented by concrete class) ---

    @abstractmethod
    async def create(self, entity: ConversationEntity) -> ConversationEntity:
        """Adds a new conversation to the persistence store."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, entity: ConversationEntity) -> ConversationEntity:
        """Updates an existing conversation."""
        raise NotImplementedError

    @abstractmethod
    async def delete_by_uid(self, uid: UUID) -> None:
        """Deletes a conversation by its unique identifier."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_uid(self, uid: UUID, load_messages: bool = False) -> Optional[ConversationEntity]:
        """
        Finds a conversation entry by its unique identifier.
        Optionally loads associated messages.
        """
        raise NotImplementedError

    # --- Specific Methods for ConversationRepository ---

    @abstractmethod
    async def find_by_bot_uids(
        self,
        bot_uids: List[UUID],
        load_messages: bool = False # Option to load messages
        ) -> List[ConversationEntity]:
        """Finds all conversations associated with the given bot UIDs."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_bot_uids_and_platform(
        self,
        bot_uids: List[UUID],
        platform: ChatPlatform, # Use Enum if defined
        load_messages: bool = False
        ) -> List[ConversationEntity]:
        """Finds conversations for specific bots filtered by platform."""
        raise NotImplementedError

    @abstractmethod
    async def find_single_by_bot_uid_and_platform(
        self,
        bot_uid: UUID,
        platform: ChatPlatform, # Use Enum if defined
        load_messages: bool = True # Usually want messages for single view
        ) -> Optional[ConversationEntity]:
        """Finds a single conversation for a specific bot and platform."""
        raise NotImplementedError

    async def find_by_platform_and_sender_id(
            self,
            platform: str,
            sender_id: str,
            bot_uid: UUID) -> Optional[
        ConversationEntity]:
        raise NotImplementedError


