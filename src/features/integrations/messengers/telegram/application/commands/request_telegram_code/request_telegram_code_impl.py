# src/features/integrations/messengers/telegram/application/commands/request_telegram_code/request_telegram_code_impl.py

import uuid
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass

from src.core.base.command import BaseCommandHandler
from src.features.bot.application.services.bot_access_service import BotAccessService
from src.features.integrations.messengers.telegram.application.services.telethon_client_service import TelethonClientService
from src.features.integrations.messengers.telegram.domain.uow.telegram_unit_of_work import TelegramUnitOfWork
from src.features.integrations.messengers.telegram.application.commands.request_telegram_code.request_telegram_code_command import RequestTelegramCodeCommand
from src.features.integrations.messengers.telegram.api.v1.dtos.telegram_auth_dtos import RequestTelegramCodeResponseDTO
from src.features.integrations.messengers.telegram.domain.entities.telegram_account_link_entity import TelegramAccountLinkEntity
from src.features.integrations.messengers.telegram.exceptions.telegram_exceptions import (
    TelegramRateLimitError, TelegramAuthError, TelegramGenericError
)



@dataclass
class RequestTelegramCodeCommandHandler(BaseCommandHandler[RequestTelegramCodeCommand, RequestTelegramCodeResponseDTO]):

    _telethon_service: TelethonClientService
    _unit_of_work: TelegramUnitOfWork
    _bot_access_service: BotAccessService
    _allowed_roles: list[str]

    async def __call__(self, command: RequestTelegramCodeCommand) -> RequestTelegramCodeResponseDTO:
        logger.info(f"Requesting Telegram code for phone {command.phone_number}, bot {command.bot_uid}")

        # ✅ Bot access check done here
        target_bot = await self._bot_access_service.check_single_bot_access(
            command.current_user.uid, command.bot_uid, allowed_roles=self._allowed_roles
        )

        try:
            result = await self._telethon_service.request_login_code(phone_number=command.phone_number)
            phone_code_hash = result["phone_code_hash"]
            temporary_session_string = result["temporary_session_string"]

            async with self._unit_of_work:
                link = await self._unit_of_work.account_link_repository.find_by_phone_number(command.phone_number)

                if not link:
                    link = TelegramAccountLinkEntity(
                        uid=uuid.uuid4(),
                        bot_uid=command.bot_uid,
                        platform_user_uid=command.current_user.uid,
                        phone_number=command.phone_number,
                        telegram_user_id=None,
                        session_string=temporary_session_string,
                        phone_code_hash=phone_code_hash,
                        is_active=False,
                    )
                    await self._unit_of_work.account_link_repository.create(link)
                else:
                    link.bot_uid = command.bot_uid
                    link.platform_user_uid = command.current_user.uid
                    link.set_phone_code_hash(phone_code_hash, temporary_session_string)
                    await self._unit_of_work.account_link_repository.update(link)

            return RequestTelegramCodeResponseDTO(phone_code_hash=phone_code_hash)

        except (TelegramRateLimitError, TelegramAuthError, TelegramGenericError) as e:
            logger.error(f"Telegram error: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            raise TelegramGenericError(f"Failed to send code: {str(e)}")
