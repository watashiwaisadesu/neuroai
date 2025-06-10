from fastapi import Depends

from src.features.bot.application.services.bot_access_service import BotAccessService
from src.features.bot.application.services.bot_platform_linker_service import BotPlatformLinkerService
from src.features.bot.application.services.bot_platform_linker_service_impl import BotPlatformLinkerServiceHandler
from src.features.bot.dependencies import get_bot_unit_of_work
from src.features.bot.domain.repositories.bot_unit_of_work import BotUnitOfWork


def get_bot_access_service(
    uow: BotUnitOfWork = Depends(get_bot_unit_of_work)
) -> BotAccessService:
    """Provides an instance of the BotAccessService."""
    return BotAccessService(uow=uow)


async def get_bot_platform_linker_service(
    uow: BotUnitOfWork = Depends(get_bot_unit_of_work)
) -> BotPlatformLinkerService:
    """
    Factory function to create and return an instance of BotPlatformLinkerService.
    """

    return BotPlatformLinkerServiceHandler(bot_uow=uow)