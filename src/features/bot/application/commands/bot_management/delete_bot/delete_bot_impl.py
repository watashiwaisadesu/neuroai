# src/features/bot/application/commands/bot_management/delete_bot/delete_bot_command_handler.py
from dataclasses import dataclass, field

from src.core.base.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.features.bot.api.v1.dtos.delete_bot_dto import DeleteBotResponseDTO
from src.features.bot.api.v1.dtos.minimal_bot_dto import MinimalBotDTO
from src.features.bot.application.commands.bot_management.delete_bot.delete_bot_command import DeleteBotCommand
from src.features.bot.application.mappers.minimal_bot_dto_mapper import MinimalBotDTOMapper
from src.features.bot.application.services.bot_access_service import BotAccessService
from src.features.bot.domain.entities.bot_entity import BotEntity
from src.features.bot.domain.repositories.bot_unit_of_work import BotUnitOfWork


@dataclass
class DeleteBotCommandHandler(BaseCommandHandler[DeleteBotCommand, DeleteBotResponseDTO]):
    _unit_of_work: BotUnitOfWork
    _access_service: BotAccessService
    _mediator: Mediator
    _allowed_roles: list[str]

    _minimal_bot_dto_mapper: MinimalBotDTOMapper = field(init=False, repr=False)

    def __post_init__(self):
        self._minimal_bot_dto_mapper = MinimalBotDTOMapper(BotEntity, MinimalBotDTO)


    async def __call__(self, command: DeleteBotCommand) -> DeleteBotResponseDTO:
        async with self._unit_of_work:
            bot = await self._access_service.check_single_bot_access(
                user_uid=command.user_uid,
                bot_uid=command.bot_uid,
                allowed_roles=self._allowed_roles
            )
            delete_bot_dto = self._minimal_bot_dto_mapper.to_dto(bot)

            # Delete the bot
            await self._unit_of_work.bot_repository.delete_by_uid(command.bot_uid)


        # You could publish a BotDeletedEvent here if needed
        # await self._mediator.publish(BotDeletedEvent(bot_uid=str(bot.uid), deleted_by=command.user_uid))

        # return DeleteBotResponseDTO(bot=delete_bot_dto)
        return DeleteBotResponseDTO(
                message=f"bot {bot.uid} deleted successfully",
                bot=MinimalBotDTO(**delete_bot_dto.model_dump())
            )