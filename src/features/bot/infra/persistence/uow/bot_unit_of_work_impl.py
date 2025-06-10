from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.features.bot.domain.repositories.bot_document_repository import BotDocumentRepository
from src.features.bot.domain.repositories.bot_participant_repository import BotParticipantRepository
from src.features.bot.domain.repositories.bot_repository import BotRepository
from src.features.bot.domain.repositories.bot_service_repository import BotServiceRepository
from src.features.bot.domain.repositories.bot_unit_of_work import BotUnitOfWork


class BotUnitOfWorkImpl(BotUnitOfWork):
    def __init__(
            self,
            session: AsyncSession,
            bot_repository: BotRepository,
            bot_service_repository: Optional[BotServiceRepository] = None,
            bot_participant_repository: Optional[BotParticipantRepository] = None,
            bot_document_repository: Optional[BotDocumentRepository] = None,
    ) -> None:
        self._session: AsyncSession = session
        self.bot_repository: BotRepository = bot_repository
        self.bot_service_repository: Optional[BotServiceRepository] = bot_service_repository
        self.bot_participant_repository: Optional[BotParticipantRepository] = bot_participant_repository
        self.bot_document_repository: Optional[BotDocumentRepository] = bot_document_repository

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()
        await self._session.close()

    async def begin(self) -> None:
        await self._session.begin()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
