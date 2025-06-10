from abc import ABC, abstractmethod

from src.core.base.unit_of_work import BaseUnitOfWork
from src.features.bot.domain.repositories.bot_document_repository import BotDocumentRepository
from src.features.bot.domain.repositories.bot_participant_repository import BotParticipantRepository
from src.features.bot.domain.repositories.bot_repository import BotRepository
from src.features.bot.domain.repositories.bot_service_repository import BotServiceRepository


class BotUnitOfWork(BaseUnitOfWork[BotRepository]):
    bot_repository: BotRepository
    bot_service_repository: BotServiceRepository
    bot_participant_repository: BotParticipantRepository
    bot_document_repository: BotDocumentRepository

    async def __aenter__(self): ...
    async def __aexit__(self, exc_type, exc_val, exc_tb): ...

    @abstractmethod
    async def begin(self):
        ...

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...