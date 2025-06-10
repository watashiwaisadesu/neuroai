# src/features/bot/application/commands/bot_participants/unlink_participant/unlink_participant_command_handler.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass

from src.core.mediator.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.features.bot.api.v1.dtos.remove_bot_participant_dto import UnlinkBotParticipantResponseDTO
from src.features.bot.application.commands.bot_participants.unlink_participant.unlink_participant_command import \
    UnlinkBotParticipantCommand
from src.features.bot.application.services.bot_access_service import BotAccessService
from src.features.bot.domain.repositories.bot_unit_of_work import BotUnitOfWork
from src.features.bot.exceptions.bot_exceptions import (
    ParticipantNotFoundError,
    CannotUnlinkOwnerError
)




@dataclass
class UnlinkBotParticipantCommandHandler(
    BaseCommandHandler[UnlinkBotParticipantCommand, UnlinkBotParticipantResponseDTO]):
    """Handler for removing a participant from a bot."""

    _unit_of_work: BotUnitOfWork
    _access_service: BotAccessService
    _mediator: Mediator
    _allowed_roles: list[str]

    async def __call__(self, command: UnlinkBotParticipantCommand) -> UnlinkBotParticipantResponseDTO:
        """
        Handles removing a participant:
        1. Validates access permissions
        2. Checks if the user to remove is the bot owner
        3. Deletes the participant record
        4. Returns a success message
        """
        logger.info(
            f"Attempting to remove participant user '{command.participant_user_uid}' from bot '{command.bot_uid}'")

        target_bot = await self._access_service.check_single_bot_access(
            user_uid=command.current_user_uid,
            bot_uid=command.bot_uid,
            allowed_roles=self._allowed_roles
        )

        # Prevent removing the owner
        if command.participant_user_uid == target_bot.user_uid:
            logger.warning(
                f"Attempt denied: Trying to remove owner (User UID: {command.participant_user_uid}) from bot {command.bot_uid}.")
            raise CannotUnlinkOwnerError("Cannot remove the bot owner from participants.")

        async with self._unit_of_work:

            # Find the participant to ensure they exist
            participant = await self._unit_of_work.bot_participant_repository.find_by_bot_and_user(
                bot_uid=command.bot_uid,
                user_uid=command.participant_user_uid
            )

            if not participant:
                logger.warning(f"Participant user {command.participant_user_uid} not found in bot {command.bot_uid}.")
                raise ParticipantNotFoundError(f"User {command.participant_user_uid} is not a participant in this bot.")

            # Delete the participant
            deleted = await self._unit_of_work.bot_participant_repository.delete_by_uid(
                bot_uid=command.bot_uid,
                user_uid=command.participant_user_uid
            )

            if not deleted:
                logger.error(f"Failed to delete participant {command.participant_user_uid} from bot {command.bot_uid}.")
                raise RuntimeError("Failed to remove participant.")

        logger.info(
            f"Successfully removed participant user {command.participant_user_uid} from bot {command.bot_uid}.")

        # Return success response
        return UnlinkBotParticipantResponseDTO(
            message=f"Successfully removed participant from bot."
        )