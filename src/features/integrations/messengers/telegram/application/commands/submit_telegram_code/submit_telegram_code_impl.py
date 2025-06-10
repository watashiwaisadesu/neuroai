# src/features/integrations/messengers/telegram/application/commands/submit_telegram_code/submit_telegram_code_handler.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass
from typing import Dict, Any, Optional

from src.core.mediator.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.features.bot.application.services.bot_access_service import BotAccessService
from src.features.conversation.domain.enums import ChatPlatform
from src.features.integrations.messengers.telegram.application.commands.submit_telegram_code.submit_telegram_code_command import SubmitTelegramCodeCommand
from src.features.integrations.messengers.telegram.api.v1.dtos.telegram_auth_dtos import SubmitTelegramCodeResponseDTO
from src.features.integrations.messengers.telegram.application.services.telethon_client_service import TelethonClientService
from src.features.integrations.messengers.telegram.application.services.telegram_event_handler_service import TelegramEventHandlerService
from src.features.integrations.messengers.telegram.domain.uow.telegram_unit_of_work import TelegramUnitOfWork
from src.features.bot.application.services.bot_platform_linker_service import BotPlatformLinkerService
from src.features.integrations.messengers.telegram.exceptions.telegram_exceptions import TelegramAuthError, TelegramGenericError, TelegramResourceNotFoundError




@dataclass
class SubmitTelegramCodeCommandHandler(BaseCommandHandler[SubmitTelegramCodeCommand, SubmitTelegramCodeResponseDTO]):
    _unit_of_work: TelegramUnitOfWork
    _telethon_service: TelethonClientService
    _event_handler_service: TelegramEventHandlerService
    _bot_platform_linker_service: BotPlatformLinkerService
    _bot_access_service: BotAccessService
    _mediator: Mediator
    _allowed_roles: list[str]

    async def __call__(self, command: SubmitTelegramCodeCommand) -> SubmitTelegramCodeResponseDTO:
        logger.info(f"Handling SubmitTelegramCodeCommand for phone {command.phone_number}, bot {command.target_bot_uid}")
        final_session_string: Optional[str] = None
        telegram_api_user_id_str: Optional[str] = None
        username_str: Optional[str] = None

        target_bot_entity = await self._bot_access_service.check_single_bot_access(
            user_uid=command.current_user.uid,
            bot_uid=command.target_bot_uid,
            allowed_roles=self._allowed_roles,
        )

        try:
            async with self._unit_of_work:
                link = await self._unit_of_work.account_link_repository.find_by_phone_number(command.phone_number)
                if not link or not link.session_string:
                    raise TelegramResourceNotFoundError("Code request not found or session is missing")

                if link.bot_uid != target_bot_entity.uid:
                    raise TelegramAuthError(f"Code is not for the specified bot.This telegram account is already in use with bot:{link.bot_uid}."
                                            f" IF you want to reassign here is telegram account link uid:{link.uid}")

                login_result = await self._telethon_service.submit_login_code(
                    phone_number=command.phone_number,
                    code=command.code,
                    phone_code_hash=link.phone_code_hash,
                    temporary_session_string=link.session_string,
                )

                final_session_string = login_result["final_session_string"]
                telegram_api_user_id_str = str(login_result["telegram_user_id"])
                username_str = login_result.get("username")

                link.activate_session(final_session_string, telegram_api_user_id_str, username_str)
                await self._unit_of_work.account_link_repository.update(link)

            service_details: Dict[str, Any] = {
                "user_label": f"Telegram ({username_str or command.phone_number})",
                "display_telegram_api_id": telegram_api_user_id_str,
                "display_username": username_str,
                "display_phone_number": command.phone_number,
            }

            service = await self._bot_platform_linker_service.ensure_platform_service_active(
                target_bot_entity=target_bot_entity,
                platform=ChatPlatform.TELEGRAM,
                linked_account_uid=link.uid,
                service_details=service_details,
            )

            if final_session_string:
                await self._telethon_service.start_message_listener(
                    session_string=final_session_string,
                    bot_uid=target_bot_entity.uid,
                    service_uid=service.uid,
                    event_handler_service=self._event_handler_service,
                )

            return SubmitTelegramCodeResponseDTO(
                telegram_user_id=telegram_api_user_id_str,
                bot_uid=target_bot_entity.uid
            )

        except Exception as e:
            logger.exception("Unexpected error in SubmitTelegramCodeCommandHandler")
            raise TelegramGenericError(str(e)) from e