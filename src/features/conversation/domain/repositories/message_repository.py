from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.features.conversation.domain.entities.message_entity import MessageEntity  # Adjust import path

class IMessageRepository(ABC):
    @abstractmethod
    async def create(self, entity: MessageEntity, conversation_uid: UUID) -> MessageEntity:
        """Creates a new Message record associated with a conversation."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, entity: MessageEntity) -> MessageEntity:
        """Updates an existing Message record."""
        raise NotImplementedError

    @abstractmethod
    async def get(self, uid: UUID) -> Optional[MessageEntity]:
        """Retrieves a Message by its UID."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_conversation_uid(self, conversation_uid: UUID) -> List[MessageEntity]:
        """Finds all messages associated with a given conversation UID."""
        raise NotImplementedError

    # Add other methods as needed (e.g., delete)