# src/features/bot/domain/repositories/bot_participant_repository.py

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

# Import the domain entity
from src.features.bot.domain.entities.bot_participant_entity import BotParticipantEntity

class BotParticipantRepository(ABC):
    """Abstract interface for Bot Participant data access."""

    @abstractmethod
    async def create(self, entity: BotParticipantEntity) -> BotParticipantEntity:
        """Adds a new participant to the persistence store."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_bot_and_user(self, bot_uid: UUID, user_uid: UUID) -> Optional[BotParticipantEntity]:
        """Finds a participant by bot and user UID."""
        raise NotImplementedError

    @abstractmethod
    async def find_participant_role(self, bot_uid: UUID, user_uid: UUID) -> Optional[str]:
        """Finds the role of a specific participant, returns None if not found."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_bot_uid(self, bot_uid: UUID) -> List[BotParticipantEntity]:
        """Finds all participants associated with a specific bot."""
        raise NotImplementedError

    @abstractmethod
    async def find_bots_by_user_uid(self, user_uid: UUID) -> List[BotParticipantEntity]:
        """Finds all participant entries for a specific user."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, entity: BotParticipantEntity) -> BotParticipantEntity:
        """Updates an existing participant (e.g., their role)."""
        raise NotImplementedError

    @abstractmethod
    async def delete_by_uid(self, bot_uid: UUID, user_uid: UUID) -> bool:
        """Deletes a participant entry by bot and user UID. Returns True if deleted, False otherwise."""
        raise NotImplementedError

    @abstractmethod
    async def is_participant(self, bot_uid: UUID, user_uid: UUID) -> bool:
        raise NotImplementedError

