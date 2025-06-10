# src/features/bot/application/commands/bot_management/duplicate_bot/duplicate_bot_command_handler.py
import uuid
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass

from src.core.mediator.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.features.bot.api.v1.dtos.get_user_bots_dto import BotResponseDTO
from src.features.bot.application.commands.bot_management.duplicate_bot.duplicate_bot_command import DuplicateBotCommand
from src.features.bot.application.services.bot_access_service import BotAccessService
from src.features.bot.application.services.user_lookup_service import UserLookupService
from src.features.bot.domain.entities.bot_entity import BotEntity, BotStatus
from src.features.bot.domain.entities.bot_participant_entity import BotParticipantEntity
from src.features.bot.domain.entities.bot_service_entity import BotServiceEntity
from src.features.bot.domain.enums import OWNER_ROLE_VALUE
from src.features.bot.domain.repositories.bot_unit_of_work import BotUnitOfWork
from src.features.bot.domain.value_objects.bot_quota_vo import BotQuota
from src.features.bot.utils import build_bot_response




@dataclass
class DuplicateBotCommandHandler(BaseCommandHandler[DuplicateBotCommand, BotResponseDTO]):
    _unit_of_work: BotUnitOfWork
    _access_service: BotAccessService
    _user_lookup_service: UserLookupService
    _mediator: Mediator
    _allowed_roles: list[str]

    async def __call__(self, command: DuplicateBotCommand) -> BotResponseDTO:
        """Handles the bot duplication request with access control."""
        new_owner = await self._user_lookup_service.find_user_by_email("sss")
        original_bot = await self._access_service.check_single_bot_access(
            user_uid=command.user_uid,
            bot_uid=command.bot_uid,
            allowed_roles=self._allowed_roles
        )
        logger.info(f"Duplicating bot {original_bot.uid} for user {command.user_uid}")

        # Generate unique name
        unique_suffix = str(uuid.uuid4()).split('-')[0]
        generated_name = f"{original_bot.name}_copy_{unique_suffix}" if original_bot.name else f"untitled_copy_{unique_suffix}"
        logger.debug(f"Generated name for duplicate bot: {generated_name}")

        # Create new quota
        new_quota = BotQuota(
            token_limit=original_bot.quota.token_limit,
            tokens_left=original_bot.quota.token_limit
        )

        # Generate UID for new bot explicitly
        new_bot_uid = uuid.uuid4()

        # Create new bot entity with explicit UID
        try:
            new_bot = BotEntity(
                uid=new_bot_uid,  # Explicitly set UID
                user_uid=command.user_uid,
                bot_type=original_bot.bot_type,
                ai_settings=original_bot.ai_settings,  # Copy settings
                quota=new_quota,
                name=generated_name,
                status=BotStatus.DRAFT,  # Duplicates start as draft
                tariff=original_bot.tariff,
                auto_deduction=original_bot.auto_deduction,
                crm_lead_id=None  # New bot, no CRM lead
            )
            logger.debug(f"Instantiated new duplicate BotEntity (UID: {new_bot.uid})")
        except Exception as e:
            logger.error(f"Failed to instantiate new BotEntity during duplication: {e}", exc_info=True)
            raise RuntimeError("Failed to initialize duplicate bot data.") from e

        async with self._unit_of_work:
            # Persist new bot first to ensure it's in the database
            await self._unit_of_work.bot_repository.create(new_bot)
            logger.debug(f"Persisted new bot entity with UID: {new_bot.uid}")

            # Create owner participant entry after bot is persisted
            try:
                owner_participant = BotParticipantEntity(
                    uid=uuid.uuid4(),
                    bot_uid=new_bot.uid,  # Now guaranteed to have a value
                    user_uid=command.user_uid,
                    role=OWNER_ROLE_VALUE
                )
                logger.debug(f"Instantiated owner BotParticipantEntity (UID: {owner_participant.uid})")
            except Exception as e:
                logger.error(f"Failed to instantiate owner BotParticipantEntity: {e}", exc_info=True)
                raise RuntimeError("Failed to initialize owner participant data.") from e

            # Persist participant
            await self._unit_of_work.bot_participant_repository.create(owner_participant)

            # Duplicate services
            await self._duplicate_services(original_bot.uid, new_bot.uid)


        logger.info(f"Successfully created duplicate bot (UID: {new_bot.uid}) and duplicated services.")

        # Build response
        bot_response = await build_bot_response(
            bot=new_bot,
            bot_uow=self._unit_of_work,
            user_lookup_service=self._user_lookup_service,
        )

        return BotResponseDTO(message=f"Bot duplicated successfully! Here is bot's uid: {new_bot.uid}",bot=bot_response)

    async def _duplicate_services(self, original_bot_uid: uuid.UUID, new_bot_uid: uuid.UUID):
        """Finds services of the original bot and creates copies for the new bot."""
        logger.debug(f"Fetching services for original bot UID: {original_bot_uid}")
        original_services = await self._unit_of_work.bot_service_repository.find_by_bot_uid(original_bot_uid)
        logger.debug(f"Found {len(original_services)} services to duplicate.")

        for service in original_services:
            logger.debug(f"Creating duplicate service for platform: {service.platform}")
            new_service = BotServiceEntity(
                uid=uuid.uuid4(),
                bot_uid=new_bot_uid,
                platform=service.platform,
                status="reserved"  # New services start as reserved
            )
            await self._unit_of_work.bot_service_repository.create(new_service)

        logger.debug("Finished creating duplicate service entries.")