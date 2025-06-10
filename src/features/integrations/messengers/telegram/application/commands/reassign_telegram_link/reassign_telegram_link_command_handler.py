# src/features/integrations/messengers/telegram/application/commands/reassign_telegram_link/reassign_telegram_link_handler.py (New File)

import uuid
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass

from src.core.mediator.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.features.integrations.messengers.telegram.api.v1.dtos.reassign_telegram_link_dto import \
    TelegramAccountLinkResponseDTO
from src.features.bot.application.services.bot_access_service import BotAccessService
from src.features.integrations.messengers.telegram.application.services.telegram_event_handler_service import \
    TelegramEventHandlerService
from src.features.integrations.messengers.telegram.application.services.telethon_client_service import \
    TelethonClientService
from src.features.integrations.messengers.telegram.domain.uow.telegram_unit_of_work import TelegramUnitOfWork
from src.features.integrations.messengers.telegram.application.commands.reassign_telegram_link.reassign_telegram_link_command import ReassignTelegramLinkCommand
from src.features.integrations.messengers.telegram.exceptions.telegram_exceptions import (
    TelegramResourceNotFoundError, TelegramAuthError
)



@dataclass
class ReassignTelegramLinkCommandHandler(BaseCommandHandler[ReassignTelegramLinkCommand, TelegramAccountLinkResponseDTO]):
    _unit_of_work: TelegramUnitOfWork
    _bot_access_service: BotAccessService
    _allowed_roles: list[str]
    _mediator: Mediator
    _telethon_service: TelethonClientService
    _event_handler_service: TelegramEventHandlerService


    async def __call__(self, command: ReassignTelegramLinkCommand) -> TelegramAccountLinkResponseDTO:
        logger.info(f"Attempting to reassign Telegram link {command.link_uid} to new bot {command.new_bot_uid}")

        async with self._unit_of_work:
            # 1. Find the existing Telegram Account Link
            service_uid = uuid.UUID(command.link_uid)
            existing_link = await self._unit_of_work.account_link_repository.find_by_uid(service_uid)

            if not existing_link:
                logger.warning(f"Telegram link {command.link_uid} not found for reassignment.")
                raise TelegramResourceNotFoundError(f"Telegram link with UID {command.link_uid} not found.")

            # 2. Check access to the CURRENT bot (if any) associated with the link
            if existing_link.bot_uid:
                try:
                    await self._bot_access_service.check_single_bot_access(
                        command.current_user.uid, existing_link.bot_uid, self._allowed_roles
                    )
                except Exception as e: # Catch broader exception for access service
                    logger.warning(f"User {command.current_user.uid} denied access to current bot {existing_link.bot_uid} for link {command.link_uid}.")
                    raise TelegramAuthError(f"Unauthorized to reassign link from current bot: {e}")

            # 3. Check access to the NEW bot
            try:
                new_bot_entity = await self._bot_access_service.check_single_bot_access(
                    command.current_user.uid, command.new_bot_uid, self._allowed_roles
                )
            except Exception as e:
                logger.warning(f"User {command.current_user.uid} denied access to new bot {command.new_bot_uid} for link {command.link_uid}.")
                raise TelegramAuthError(f"Unauthorized to reassign link to new bot: {e}")

            # 4. Perform the reassignment
            if existing_link.bot_uid == command.new_bot_uid:
                logger.info(f"Telegram link {command.link_uid} is already assigned to bot {command.new_bot_uid}. No change needed.")
                # You might choose to raise an error here or just return success
                return TelegramAccountLinkResponseDTO.from_entity(existing_link)


            existing_link.bot_uid = command.new_bot_uid
            # Optionally, update platform_user_uid if the reassigner is different from original linker
            existing_link.platform_user_uid = command.current_user.uid # Reassign to current user who initiated it

            await self._unit_of_work.account_link_repository.update(existing_link)
            logger.info(f"Telegram link {command.link_uid} successfully reassigned from {existing_link.bot_uid} to {command.new_bot_uid}.")

            # 5. Handle active sessions/listeners (CRITICAL)
            # If the link is active and attached to an old bot, you might need to:
            # - Stop the old Telethon client listener associated with the OLD bot.
            # - Start a new Telethon client listener associated with the NEW bot.
            # This would involve injecting TelethonClientService here and adding methods for stop/start.
            # For simplicity, I'm omitting this complex part, but it's important for live systems.
            # Example:
            if existing_link.is_active:
                await self._telethon_service.stop_message_listener(service_uid=service_uid)
                await self._telethon_service.start_message_listener(
                    session_string=existing_link.session_string,
                    bot_uid=new_bot_entity.uid,
                    service_uid=service_uid,
                    event_handler_service=self._event_handler_service, # Need to inject this too
                )


        return TelegramAccountLinkResponseDTO.from_entity(existing_link)