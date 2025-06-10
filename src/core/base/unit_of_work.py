from abc import ABC, abstractmethod
from typing import TypeVar, Generic

_T = TypeVar('_T')

class BaseUnitOfWork(ABC, Generic[_T]):

    @abstractmethod
    async def __aenter__(self):
        """Asynchronously enters the runtime context related to this object."""
        raise NotImplementedError()

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Asynchronously exits the runtime context related to this object."""
        raise NotImplementedError()

    @abstractmethod
    def commit(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError()