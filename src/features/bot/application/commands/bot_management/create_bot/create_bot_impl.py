# 2. Command Handler (src/features/bot/application/commands/bot_management/create_bot/create_bot_command_handler.py)
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
import uuid
from dataclasses import dataclass, field

from src.core.base.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.features.bot.api.v1.dtos.create_bot_dto import CreateBotResponseDTO
from src.features.bot.api.v1.dtos.minimal_bot_dto import MinimalBotDTO

from src.features.bot.application.commands.bot_management.create_bot.create_bot_command import CreateBotCommand
from src.features.bot.application.mappers.minimal_bot_dto_mapper import MinimalBotDTOMapper
from src.features.bot.domain.entities.bot_entity import BotEntity
from src.features.bot.domain.entities.bot_participant_entity import BotParticipantEntity
from src.features.bot.domain.enums import OWNER_ROLE_VALUE
from src.features.bot.domain.events.bot_events import (
    BotExpirySetEvent
)
from src.features.bot.domain.repositories.bot_unit_of_work import BotUnitOfWork
from src.features.bot.domain.value_objects.ai_configuration_vo import AIConfigurationSettings
from src.features.bot.domain.value_objects.bot_quota_vo import BotQuota




@dataclass
class CreateBotCommandHandler(BaseCommandHandler[CreateBotCommand, CreateBotResponseDTO]):
    _unit_of_work: BotUnitOfWork
    _mediator: Mediator

    _minimal_bot_dto_mapper: MinimalBotDTOMapper = field(init=False, repr=False)

    def __post_init__(self):
        self._minimal_bot_dto_mapper = MinimalBotDTOMapper(BotEntity, MinimalBotDTO)

    async def __call__(self, command: CreateBotCommand) -> CreateBotResponseDTO:
        logger.info(f"Creating bot of type '{command.bot_type}' for user {command.user_uid}")

        # Create default Value Objects
        default_ai_settings = AIConfigurationSettings()
        default_quota = BotQuota()

        # Create bot entity
        bot = BotEntity(
            user_uid=uuid.UUID(command.user_uid),
            bot_type=command.bot_type,
            ai_settings=default_ai_settings,
            quota=default_quota,
        )



        # Persist within transaction
        async with self._unit_of_work as uow:
            bot = await uow.bot_repository.create(bot)


        async with self._unit_of_work as uow:
            # Create owner participant
            owner_participant = BotParticipantEntity(
                bot_uid=bot.uid,
                user_uid=uuid.UUID(command.user_uid),
                role=OWNER_ROLE_VALUE
            )
            await uow.bot_participant_repository.create(owner_participant)
            # Publish domain events
            events = [
                BotExpirySetEvent(
                    bot_uid=str(bot.uid),
                    expiry_seconds=1800  # 30 minutes
                )
            ]

            await self._mediator.publish(events)

        bot_dto = self._minimal_bot_dto_mapper.to_dto(bot)
        logger.info(f"Bot created successfully with UID: {bot.uid}")

        return CreateBotResponseDTO(
            message=f"{command.bot_type} bot created successfully",
            bot=MinimalBotDTO(**bot_dto.model_dump())
        )