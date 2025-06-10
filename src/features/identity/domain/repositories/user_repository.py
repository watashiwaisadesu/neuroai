from abc import abstractmethod
from typing import List
from uuid import UUID

from src.core.base.repository import BaseRepository
from src.features.identity.domain.entities.user_entity import UserEntity


class UserRepository(BaseRepository[UserEntity]):

    @abstractmethod
    async def find_by_email(self, email: str) -> UserEntity:
        raise NotImplementedError()

    @abstractmethod
    async def find_by_uids(self, uids: List[UUID]) -> List[UserEntity]:
        """Finds multiple users by their UIDs."""
        raise NotImplementedError

