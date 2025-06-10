from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# from src.features.bot.application.commands.bot_services.unlink_service.unlink_service_impl import \
#     UnlinkServiceCommandImpl
from src.features.bot.domain.repositories.bot_repository import BotRepository
from src.features.bot.domain.repositories.bot_service_repository import BotServiceRepository
from src.features.bot.domain.repositories.bot_unit_of_work import BotUnitOfWork
from src.features.bot.infra.persistence.repositories.bot_document_repository_impl import BotDocumentRepositoryImpl
from src.features.bot.infra.persistence.repositories.bot_participant_repository_impl import BotParticipantRepositoryImpl
from src.features.bot.infra.persistence.repositories.bot_repository_impl import BotRepositoryImpl
from src.features.bot.infra.persistence.repositories.bot_service_repository_impl import BotServiceRepositoryImpl
from src.features.bot.infra.persistence.uow.bot_unit_of_work_impl import BotUnitOfWorkImpl
from src.infra.persistence.connection.sqlalchemy_engine import get_async_db


async def get_bot_repository(session: AsyncSession) -> BotRepository:
    return BotRepositoryImpl(session)


async def get_bot_service_repository(
    session: AsyncSession,
) -> BotServiceRepository:
    return BotServiceRepositoryImpl(session)


async def get_bot_participant_repository(
        session: AsyncSession,
):
    return BotParticipantRepositoryImpl(session)

async def get_bot_document_repository(
        session: AsyncSession,
):
    return BotDocumentRepositoryImpl(session)



async def get_bot_unit_of_work(
    session: AsyncSession = Depends(get_async_db),
) -> BotUnitOfWork:
    bot_repo = await get_bot_repository(session)
    bot_service_repo = await get_bot_service_repository(session)
    participant_repo = await get_bot_participant_repository(session)
    bot_document_repo = await  get_bot_document_repository(session)
    return BotUnitOfWorkImpl(session, bot_repo, bot_service_repo, bot_participant_repository=participant_repo, bot_document_repository=bot_document_repo)


