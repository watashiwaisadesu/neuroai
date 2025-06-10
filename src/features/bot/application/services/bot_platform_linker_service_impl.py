# src/features/bot/application/services/bot_platform_linker_service_impl.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from uuid import UUID  # Not strictly needed here anymore if not creating UID, but BotServiceEntity might use it
from typing import Dict, Any, Optional

from src.features.bot.application.services.bot_platform_linker_service import \
    BotPlatformLinkerService  # Assuming interface
from src.features.bot.domain.entities.bot_entity import BotEntity
from src.features.bot.domain.entities.bot_service_entity import BotServiceEntity
from src.features.bot.domain.repositories.bot_unit_of_work import BotUnitOfWork
from src.features.conversation.domain.enums import ChatPlatform
# Import a suitable exception
from src.features.bot.exceptions.bot_exceptions import ServiceNotFoundError  # Or a new ReservedServiceNotFoundError




class BotPlatformLinkerServiceHandler(BotPlatformLinkerService):  # Implement your interface
    def __init__(self, bot_uow: BotUnitOfWork):
        self._bot_uow = bot_uow
        logger.debug("BotPlatformLinkerServiceImpl initialized.")

    async def ensure_platform_service_active(
            # Method name might be slightly misleading now, could be activate_reserved_service
            self,
            target_bot_entity: BotEntity,
            platform: ChatPlatform,
            linked_account_uid: UUID,
            service_details: Optional[Dict[str, Any]] = None
    ) -> BotServiceEntity:
        platform_name_str = platform.value
        bot_uid = target_bot_entity.uid
        desired_status = "active"

        logger.info(
            f"Attempting to activate 'reserved' service for platform '{platform_name_str}' for bot '{bot_uid}'."
        )

        activated_service: Optional[BotServiceEntity] = None

        async with self._bot_uow:  # UoW context manager handles commit/rollback
            service_to_activate: Optional[BotServiceEntity] = None
            # Ensure your repository has this method
            if hasattr(self._bot_uow.bot_service_repository, 'find_first_by_bot_platform_status'):
                service_to_activate = await self._bot_uow.bot_service_repository.find_first_by_bot_platform_status(
                    bot_uid=bot_uid,
                    platform=platform_name_str,
                    status="reserved",
                )
            else:
                logger.critical(  # This is a critical setup issue if the method is expected
                    "BotServiceRepository does not implement 'find_first_by_bot_platform_status'. "
                    "Cannot find 'reserved' service."
                )
                raise NotImplementedError("Required repository method 'find_first_by_bot_platform_status' is missing.")

            if service_to_activate:
                logger.info(
                    f"Found 'reserved' service (UID: {service_to_activate.uid}) for bot {bot_uid}, "
                    f"platform '{platform_name_str}'. Activating and updating with provided config."
                )
                service_to_activate.status = desired_status
                service_to_activate.linked_account_uid = linked_account_uid

                if hasattr(service_to_activate, 'service_details'):
                    if service_details is not None:
                        # You might want to merge if config_details can be partially updated
                        # For now, let's assume full replacement or setting if None.
                        service_to_activate.service_details = service_details
                    elif service_to_activate.config_details is None:  # Ensure it's at least an empty dict if not provided
                        service_to_activate.config_details = {}
                    logger.info(f"Applied details_for_config to service UID {service_to_activate.uid}.")
                else:
                    logger.warning(
                        f"Service entity (UID: {service_to_activate.uid}) lacks 'config_details'. Cannot store details_for_config.")

                if hasattr(service_to_activate, 'update_timestamp'):
                    service_to_activate.update_timestamp()

                activated_service = await self._bot_uow.bot_service_repository.update(service_to_activate)
                logger.info(
                    f"Service UID {activated_service.uid} successfully activated and config updated.")
            else:
                # **CRITICAL CHANGE**: Do not create a new service. Raise an error.
                error_message = (
                    f"No 'reserved' service found for bot {bot_uid} and platform '{platform_name_str}'. "
                    "A pre-existing 'reserved' service entry is required for this operation."
                )
                logger.error(error_message)
                raise ServiceNotFoundError(error_message)  # Or a more specific ReservedServiceNotFoundError

        if not activated_service:
            # This state should ideally not be reached if the logic above correctly raises errors
            # or if the update operation is guaranteed to return the entity or raise its own error.
            # This is a safeguard for an unexpected None without prior exception.
            critical_error_msg = f"Failed to activate service for bot {bot_uid}, platform {platform_name_str} (unexpected null after UoW)."
            logger.critical(critical_error_msg)
            raise Exception(critical_error_msg)

        return activated_service