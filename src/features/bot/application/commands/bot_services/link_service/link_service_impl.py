from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
import uuid
from dataclasses import dataclass, field

from src.core.base.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.features.bot.api.v1.dtos.bot_service_management_dto import (
    LinkServiceResponseDTO,  # The new wrapper DTO
    BotServiceDTO,  # The nested DTO
)
from src.features.bot.application.commands.bot_services.link_service.link_service_command import LinkServiceCommand
from src.features.bot.application.mappers.bot_service_dto_mapper import BotServiceDTOMapper  # Import your new mapper
from src.features.bot.application.services.bot_access_service import BotAccessService
from src.features.bot.domain.entities.bot_service_entity import BotServiceEntity  # For mapper init
from src.features.bot.domain.repositories.bot_unit_of_work import BotUnitOfWork




@dataclass
class LinkServiceCommandHandler(BaseCommandHandler[LinkServiceCommand, LinkServiceResponseDTO]): # <-- Corrected return type
    """Handler for linking a service to a bot."""

    _unit_of_work: BotUnitOfWork
    _access_service: BotAccessService
    _mediator: Mediator
    _allowed_roles: list[str]
    _bot_service_mapper: BotServiceDTOMapper = field(init=False, repr=False) # Inject the mapper

    def __post_init__(self):
        # Initialize the mapper
        self._bot_service_mapper = BotServiceDTOMapper(BotServiceEntity, BotServiceDTO)


    async def __call__(self, command: LinkServiceCommand) -> LinkServiceResponseDTO: # <-- Corrected return type
        logger.info(f"Attempting to link service '{command.request_data.platform}' to bot '{command.bot_uid}' by user '{command.current_user_uid}'")

        # 1. Validate access permissions for the current user
        target_bot = await self._access_service.check_single_bot_access(
            user_uid=command.current_user_uid,
            bot_uid=command.bot_uid,
            allowed_roles=self._allowed_roles,
        )

        async with self._unit_of_work as uow:
            # 2. Check if a service of this platform is already linked to the bot
            # Assuming you have a method to find service by bot_uid and platform
            # existing_service_link = await uow.bot_service_repository.find_by_bot_and_platform(
            #     bot_uid=target_bot.uid,
            #     platform=command.request_data.platform
            # )
            # if existing_service_link:
            #     logger.warning(f"Service platform '{command.request_data.platform}' is already linked to bot '{target_bot.uid}'.")
            #     # You might want to update it instead of raising an error, depending on business logic
            #     raise ServiceAlreadyLinkedError(f"Service platform '{command.request_data.platform}' is already linked to this bot.")

            # 3. Create the BotServiceEntity
            # Assign a new UUID for the service link record itself
            new_service_entity = BotServiceEntity(
                uid=uuid.uuid4(), # Explicitly create a new UUID for the service link record
                bot_uid=target_bot.uid,
                platform=command.request_data.platform,
                status="reserved", # Initial status, might change after external service interaction
                linked_account_uid=None # This might be set after successful linking with external platform
            )
            logger.debug(f"Creating new BotServiceEntity for bot {target_bot.uid}, platform {command.request_data.platform}")

            # 4. Persist the new service link
            created_service = await uow.bot_service_repository.create(new_service_entity)

            # Optional: Here you might initiate external service integration (e.g., call Telegram API)
            # This could be done by publishing an event (e.g., ServiceLinkRequestedEvent)
            # await self._mediator.publish(ServiceLinkRequestedEvent(created_service.uid, ...))
            # The status would then be updated by a separate handler/service.

        logger.info(f"Successfully linked service '{command.request_data.platform}' to bot '{target_bot.uid}'.")

        # 5. Map the created entity to the DTO for response
        # Use the mapper to create the nested BotServiceDTO
        service_dto = self._bot_service_mapper.to_dto(created_service)

        # 6. Return the wrapper DTO
        return LinkServiceResponseDTO(
            message=f"Service '{command.request_data.platform}' successfully linked to bot '{target_bot.uid}'. Initial status: '{created_service.status}'.",
            service=service_dto
        )