# src/features/bot/application/queries/bot_services/get_services/get_services_handler.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass, field  # Import 'field' for mapper injection
from typing import List

from src.core.mediator.query import BaseQueryHandler
from src.features.bot.api.v1.dtos.bot_service_management_dto import \
    BotServiceDTO, GetServicesResponseDTO  # Import the new response DTO and BotServiceDTO
from src.features.bot.application.mappers.bot_service_dto_mapper import BotServiceDTOMapper  # Import your mapper
from src.features.bot.application.queries.bot_services.get_services.get_services_query import GetServicesQuery
from src.features.bot.application.services.bot_access_service import BotAccessService
from src.features.bot.domain.entities.bot_service_entity import BotServiceEntity  # For mapper initialization
from src.features.bot.domain.repositories.bot_unit_of_work import BotUnitOfWork




@dataclass(kw_only=True)
class GetServicesQueryHandler(BaseQueryHandler[GetServicesQuery, GetServicesResponseDTO]): # <-- Changed return type
    _bot_uow: BotUnitOfWork
    _access_service: BotAccessService
    _allowed_roles: list[str]
    _bot_service_mapper: BotServiceDTOMapper = field(init=False, repr=False) # Inject the mapper

    def __post_init__(self):
        # Initialize the mapper
        self._bot_service_mapper = BotServiceDTOMapper(BotServiceEntity, BotServiceDTO)

    async def __call__(self, query: GetServicesQuery) -> GetServicesResponseDTO: # <-- Changed return type
        """
        Handles retrieving services linked to a bot:
        1. Validates access permissions.
        2. Fetches linked service entities.
        3. Maps services to BotServiceDTOs.
        4. Wraps results in a GetServicesResponse DTO with a message.
        """
        logger.info(f"User {query.user_uid} attempting to list services for bot UID: {query.bot_uid}")

        # 1. Validate access permissions and fetch the bot
        # This will raise BotAccessDeniedError or BotNotFoundError if access is not granted or bot doesn't exist
        target_bot = await self._access_service.check_single_bot_access(
            user_uid=query.user_uid,
            bot_uid=query.bot_uid,
            allowed_roles=self._allowed_roles
        )

        # 2. Fetch linked service entities
        async with self._bot_uow as uow: # Use UoW context
            service_entities = await uow.bot_service_repository.find_by_bot_uid(target_bot.uid)
            logger.debug(f"Found {len(service_entities)} service entities for bot {target_bot.uid}.")

        # 3. Map services to BotServiceDTOs
        mapped_services: List[BotServiceDTO] = []
        for service_entity in service_entities:
            try:
                mapped_dto = self._bot_service_mapper.to_dto(service_entity)
                mapped_services.append(mapped_dto)
            except Exception as e:
                logger.error(
                    f"Failed to map BotServiceEntity {service_entity.uid} to DTO for bot {target_bot.uid}: {e}",
                    exc_info=True
                )
                # Decide on error handling: skip, or include partial DTO, or raise
                # For now, we skip on mapping failure.

        # 4. Wrap results in a GetServicesResponse DTO with a message
        message = f"Successfully retrieved {len(mapped_services)} service(s) for bot {target_bot.uid}."
        logger.info(message)

        return GetServicesResponseDTO(
            message=message,
            services=mapped_services
        )