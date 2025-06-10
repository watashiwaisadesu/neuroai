# 2. Query Handler (src/features/bot/application/queries/bot_management/get_user_bots/get_user_bots_query_handler.py)
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass
from typing import List

from src.core.base.query import BaseQueryHandler
from src.core.mediator.mediator import Mediator
from src.features.bot.api.v1.dtos.get_user_bots_dto import BotResponseDTO, BotDTO, GetUserBotsResponse
from src.features.bot.application.queries.bot_management.get_user_bots.get_user_bots_query import GetUserBotsQuery
from src.features.bot.application.services.bot_access_service import BotAccessService
from src.features.bot.application.services.user_lookup_service import UserLookupService
# from src.features.bot.domain.events.bot_events import UserBotsQueriedEvent
from src.features.bot.domain.repositories.bot_unit_of_work import BotUnitOfWork
from src.features.bot.utils import build_bot_response





@dataclass
class GetUserBotsQueryHandler(BaseQueryHandler[GetUserBotsQuery, GetUserBotsResponse]):
    _bot_uow: BotUnitOfWork
    _user_lookup_service: UserLookupService
    _access_service: BotAccessService
    _mediator: Mediator
    _allowed_roles: list[str]

    async def __call__(self, query: GetUserBotsQuery) -> GetUserBotsResponse:
        """
        Fetches accessible bots using BotAccessService and builds response DTOs.
        Publishes an event for analytics/tracking purposes.
        """
        logger.info(f"Fetching accessible bots for user UID: {query.user_uid}")

        # Get user entity using the repository directly (no UoW context needed for reads)
        user = await self._user_lookup_service.get_user_by_uid(str(query.user_uid))
        if not user:
            logger.error(f"User {query.user_uid} not found")
            return []

        bots_data: List[BotDTO] = []

        wrappers: List[BotResponseDTO] = []

        # Use BotAccessService to get accessible bots
        try:
            accessible_bots = await self._access_service.get_accessible_bots(
                query.user_uid,
                allowed_roles=self._allowed_roles
            )
            logger.debug(f"Found {len(accessible_bots)} accessible bots")
        except Exception as e:
            logger.error(f"Error getting accessible bots: {e}", exc_info=True)
            return []

        for bot in accessible_bots:
            try:
                bot_dto = await build_bot_response(
                    bot=bot,
                    bot_uow=self._bot_uow,
                    user_lookup_service=self._user_lookup_service
                )
                if bot_dto:
                    bots_data.append(bot_dto)
                else:
                    logger.warning(f"build_bot_response returned None for bot {bot.uid}")
            except Exception as e:
                logger.error(f"Failed to build response for bot {bot.uid}: {e}", exc_info=True)

        # Publish analytics event
        # await self._mediator.publish([
        #     UserBotsQueriedEvent(
        #         user_uid=query.user_uid,
        #         bot_count=len(wrappers),
        #         bot_uids=[str(bot.bot.uid) for bot in wrappers if bot.bot]
        #     )
        # ])

        message = f"{len(bots_data)} bot(s) found for user {query.user_uid}." if bots_data else f"No bots found for user {query.user_uid}."
        logger.info(f"Returning {len(bots_data)} bot responses for user {query.user_uid}")

        return GetUserBotsResponse(
            message=message,
            bots=bots_data
        )