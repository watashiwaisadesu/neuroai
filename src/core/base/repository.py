from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

_T = TypeVar('_T')


class BaseRepository(ABC, Generic[_T]):

    @abstractmethod
    async def create(self, entity: _T) -> _T:
        raise NotImplementedError()

    @abstractmethod
    async def update(self, entity: _T) -> _T:
        raise NotImplementedError()

    @abstractmethod
    async def delete_by_uid(self, uid: UUID) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def find_by_uid(self, uid: UUID) -> _T | None:
        raise NotImplementedError()