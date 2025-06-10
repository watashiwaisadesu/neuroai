# src/features/bot/application/commands/bot_management/update_bot/update_bot_command_handler.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass, asdict

from src.core.mediator.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.features.bot.api.v1.dtos.get_user_bots_dto import BotResponseDTO
from src.features.bot.application.commands.bot_management.update_bot.update_bot_command import UpdateBotCommand
from src.features.bot.application.services.bot_access_service import BotAccessService
from src.features.bot.application.services.user_lookup_service import UserLookupService
from src.features.bot.domain.repositories.bot_unit_of_work import BotUnitOfWork
from src.features.bot.domain.value_objects.ai_configuration_vo import AIConfigurationSettings
from src.features.bot.exceptions.bot_exceptions import (
    InvalidBotAISettingsError,
    InvalidBotQuotaError, InvalidBotDetailsError
)
from src.features.bot.utils import build_bot_response




@dataclass
class UpdateBotCommandHandler(BaseCommandHandler[UpdateBotCommand, BotResponseDTO]):
    _unit_of_work: BotUnitOfWork
    _access_service: BotAccessService
    _user_lookup_service: UserLookupService
    _mediator: Mediator
    _allowed_roles: list[str]

    async def __call__(self, command: UpdateBotCommand) -> BotResponseDTO:
        """Handles bot update with access control."""
        async with self._unit_of_work:
            bot = await self._access_service.check_single_bot_access(
                user_uid=command.user_uid,
                bot_uid=command.bot_uid,
                allowed_roles=self._allowed_roles,
            )
            update_data = command.update_data.model_dump(exclude_unset=True)
            logger.debug(f"Attempting update for bot {bot.uid} with data: {update_data}")

            updated = False

            # 1. Handle AI Settings Update
            ai_settings_fields = {
                k: v for k, v in update_data.items()
                if k in AIConfigurationSettings.__annotations__
            }
            if ai_settings_fields:
                logger.debug(f"Updating AI settings for bot {bot.uid}: {ai_settings_fields}")
                current_settings_dict = asdict(bot.ai_settings)
                updated_settings_dict = {**current_settings_dict, **ai_settings_fields}
                try:
                    new_settings = AIConfigurationSettings(**updated_settings_dict)
                    bot.update_ai_settings(new_settings)
                    updated = True
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid AI settings for bot {bot.uid}: {e}")
                    raise InvalidBotAISettingsError(message=str(e)) from e

            # 2. Handle Quota Update
            if "token_limit" in update_data:
                new_limit = update_data["token_limit"]
                logger.debug(f"Updating token limit for bot {bot.uid} to: {new_limit}")
                try:
                    bot.update_token_limit(new_limit)
                    updated = True
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid token limit for bot {bot.uid}: {e}")
                    raise InvalidBotQuotaError(message=str(e)) from e

            # 3. Handle other direct Bot attribute updates
            other_bot_fields = {
                k: v for k, v in update_data.items()
                if k not in ai_settings_fields and k not in ["token_limit", "services", "reserved_services"]
            }
            if other_bot_fields:
                logger.debug(f"Updating other details for bot {bot.uid}: {other_bot_fields}")
                try:
                    bot.update_details(**other_bot_fields)
                    updated = True
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid bot details for bot {bot.uid}: {e}")
                    raise InvalidBotDetailsError(message=str(e)) from e

            # Persist if changes were made
            if updated:
                logger.info(f"Persisting updates for bot {bot.uid}")
                await self._unit_of_work.bot_repository.update(bot)
            else:
                logger.info(f"No effective changes detected for bot {bot.uid}, skipping update persistence.")

        # Build Response using UserLookupService
        logger.debug(f"Building response DTO for updated bot {bot.uid}")
        bot_response = await build_bot_response(
            bot=bot,
            bot_uow=self._unit_of_work,
            user_lookup_service=self._user_lookup_service,
        )

        return BotResponseDTO(message=f"Bot {bot.uid} updated successfully!",bot=bot_response)