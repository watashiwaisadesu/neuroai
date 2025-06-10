# src/features/bot/application/commands/unlink_service/unlink_service_impl.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from src.core.base.command import BaseCommandHandler
from src.features.bot.application.commands.bot_services.unlink_service.unlink_service_command import UnlinkServiceCommand
from src.features.bot.api.v1.dtos.bot_service_management_dto import UnlinkServiceResponseDTO
from src.features.bot.application.services.bot_access_service import BotAccessService
from src.features.bot.domain.repositories.bot_unit_of_work import BotUnitOfWork
from src.features.bot.exceptions.bot_exceptions import (
    ServiceNotFoundError,
    BotAuthorizationError
)
from src.core.mediator.mediator import Mediator
from src.features.bot.domain.events.service_unlinked_event import ServiceUnlinkedEvent




@dataclass
class UnlinkServiceCommandHandler(BaseCommandHandler[UnlinkServiceCommand, UnlinkServiceResponseDTO]):
    _unit_of_work: BotUnitOfWork
    _access_service: BotAccessService
    _mediator: Mediator
    _allowed_roles: list[str]

    async def __call__(self, command: UnlinkServiceCommand) -> UnlinkServiceResponseDTO:
        logger.info(f"Unlinking service UID {command.service_uid} from bot UID {command.bot_uid}")

        linked_account_uid: Optional[UUID] = None
        platform: Optional[str] = None

        # Step 1: Validate bot ownership and access
        bot = await self._access_service.check_single_bot_access(
            user_uid=command.current_user_uid,
            bot_uid=command.bot_uid,
            allowed_roles=self._allowed_roles
        )

        async with self._unit_of_work:
            bot_service = await self._unit_of_work.bot_service_repository.find_by_uid(command.service_uid)
            if not bot_service:
                raise ServiceNotFoundError(f"Service with UID {command.service_uid} not found.")

            if bot_service.bot_uid != bot.uid:
                raise BotAuthorizationError(f"Service {command.service_uid} does not belong to bot {bot.uid}.")

            platform = bot_service.platform
            linked_account_uid = bot_service.linked_account_uid

        # Step 2: Unlink service in DB
        async with self._unit_of_work:
            bot_service = await self._unit_of_work.bot_service_repository.find_by_uid(command.service_uid)
            if not bot_service:
                raise ServiceNotFoundError(f"Service UID {command.service_uid} disappeared mid-op.")

            bot_service.status = "reserved"
            bot_service.linked_account_uid = None

            if hasattr(bot_service, "service_details"):
                bot_service.service_details = {}

            if hasattr(bot_service, "update_timestamp"):
                bot_service.update_timestamp()

            await self._unit_of_work.bot_service_repository.update(bot_service)

        # Step 3: Publish domain event
        await self._mediator.publish([
            ServiceUnlinkedEvent(
                service_uid=command.service_uid,
                platform=platform,
                linked_account_uid=linked_account_uid
            )
        ])

        logger.info(f"Successfully unlinked service UID {command.service_uid} from bot UID {command.bot_uid}")
        return UnlinkServiceResponseDTO(
            message=f"Service {command.service_uid} unlinked from bot {command.bot_uid}.",
        )

