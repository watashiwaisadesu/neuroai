# src/features/bot/application/queries/bot_management/get_last_active_bots/get_last_active_bots_query_handler.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import List
from datetime import datetime, timezone
from dataclasses import dataclass, field # Import 'field'

from src.core.mediator.mediator import Mediator
from src.core.mediator.query import BaseQueryHandler
from src.features.bot.api.v1.dtos.get_user_bots_dto import GetLastActiveBotsResponse
# Import MinimalBotDTO as the return type
from src.features.bot.api.v1.dtos.minimal_bot_dto import MinimalBotDTO
from src.features.bot.application.queries.bot_management.get_last_active_bots.get_last_active_bots_query import \
    GetLastActiveBotsQuery
from src.features.bot.application.services.bot_access_service import BotAccessService
from src.features.bot.application.services.user_lookup_service import UserLookupService
from src.features.bot.domain.entities.bot_entity import BotEntity
from src.features.bot.domain.repositories.bot_unit_of_work import BotUnitOfWork
# Import the MinimalBotDTOMapper
from src.features.bot.application.mappers.minimal_bot_dto_mapper import MinimalBotDTOMapper




@dataclass
class GetLastActiveBotsQueryHandler(BaseQueryHandler[GetLastActiveBotsQuery, GetLastActiveBotsResponse]): # <-- Changed return type
    """Handler for getting the last 5 active bots as MinimalBotDTOs."""

    _unit_of_work: BotUnitOfWork
    _access_service: BotAccessService
    _user_lookup_service: UserLookupService
    _mediator: Mediator
    _allowed_roles: list[str]
    # Inject the MinimalBotDTOMapper
    _minimal_bot_dto_mapper: MinimalBotDTOMapper = field(init=False, repr=False)

    def __post_init__(self):
        self._minimal_bot_dto_mapper = MinimalBotDTOMapper(BotEntity, MinimalBotDTO)


    async def __call__(self, query: GetLastActiveBotsQuery) -> GetLastActiveBotsResponse: # <-- Changed return type
        """
        Handles getting last active bots:
        1. Gets all accessible bots using BotAccessService.
        2. Sorts them by updated_at descending.
        3. Takes the top 5.
        4. Maps them to MinimalBotDTOs.
        """
        logger.info(f"Fetching last active bots for user UID: {query.user_uid}")
        user = await self._user_lookup_service.get_user_by_uid(str(query.user_uid))
        if not user:
            logger.error(f"User {query.user_uid} not found")
            return []

        # We don't need `async with self._unit_of_work:` here
        # because BotAccessService and UserLookupService handle their own repository access.
        # If any direct UoW operations (create/update) were needed, the `with` block would be appropriate.

        # 1. Get all accessible bots
        try:
            # Allow any role for viewing accessible bots list (as per previous logic)
            accessible_bots = await self._access_service.get_accessible_bots(
                query.user_uid,
                allowed_roles=self._allowed_roles,
            )
            logger.debug(f"Found {len(accessible_bots)} total accessible bots.")
        except Exception as e:
            logger.error(f"Error getting accessible bots for user {query.user_uid}: {e}", exc_info=True)
            return []  # Return empty list on error

        # 2. Sort by updated_at (most recent first)
        def get_sort_key(bot: BotEntity):
            # Use updated_at timestamp, fallback to minimum datetime if None
            # Ensure the timestamp is timezone-aware for consistent sorting
            ts = getattr(bot, 'updated_at', None)
            return ts if ts else datetime.min.replace(tzinfo=timezone.utc)

        try:
            sorted_bots = sorted(accessible_bots, key=get_sort_key, reverse=True)
        except Exception as e:
            logger.error(f"Error sorting accessible bots: {e}", exc_info=True)
            sorted_bots = accessible_bots  # Proceed with unsorted if sorting fails

        # 3. Take the top 5 (or fewer if less than 5 exist)
        last_active_bots = sorted_bots[:5]
        logger.debug(f"Selected top {len(last_active_bots)} most recently updated bots.")

        # 4. Map to MinimalBotDTOs
        minimal_bot_dtos: List[MinimalBotDTO] = []
        for bot_entity in last_active_bots:
            try:
                # Use the injected MinimalBotDTOMapper
                mapped_dto = self._minimal_bot_dto_mapper.to_dto(bot_entity)
                if mapped_dto:
                    minimal_bot_dtos.append(mapped_dto)
                else:
                    logger.warning(f"MinimalBotDTOMapper returned None for bot UID {bot_entity.uid}")
            except Exception as e:
                logger.error(f"Failed to map bot {bot_entity.uid} to MinimalBotDTO: {e}", exc_info=True)
                # Skip this bot on error

        message = f"{len(minimal_bot_dtos)} last active bot(s) retrieved for user {query.user_uid}."
        logger.info(message)
        return GetLastActiveBotsResponse(
               message=message,
               bots=minimal_bot_dtos
           )