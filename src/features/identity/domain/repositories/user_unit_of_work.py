from abc import ABC, abstractmethod

from src.core.base.unit_of_work import BaseUnitOfWork
from src.features.identity.domain.repositories.user_repository import UserRepository


class UserUnitOfWork(BaseUnitOfWork[UserRepository]):
    user_repository: UserRepository

    @abstractmethod
    async def begin(self):
        ...

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...