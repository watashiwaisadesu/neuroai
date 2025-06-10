# src/features/bot/application/commands/bot_participants/link_participant/link_participant_command_handler.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
import uuid
from dataclasses import dataclass, field # Import 'field' for mapper injection
from typing import Optional

from src.core.mediator.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
# Import the specific response DTO and the nested participant DTO
from src.features.bot.api.v1.dtos.link_participant_dto import LinkBotParticipantResponseDTO, BotParticipantDTO
from src.features.bot.application.commands.bot_participants.link_participant.link_participant_command import \
    LinkBotParticipantCommand
from src.features.bot.application.mappers.bot_participant_dto_mapper import BotParticipantDTOMapper # Import your mapper
from src.features.bot.application.services.bot_access_service import BotAccessService
from src.features.bot.application.services.user_lookup_service import UserLookupService, UserInfo # Import UserInfo
from src.features.bot.domain.entities.bot_participant_entity import BotParticipantEntity
from src.features.bot.domain.repositories.bot_unit_of_work import BotUnitOfWork
from src.features.bot.exceptions.bot_exceptions import (
    CannotAddOwnerAsParticipantError, ParticipantAlreadyExistsError  # Assuming this exception exists
)
from src.features.identity.exceptions.user_exceptions import UserNotFoundError




@dataclass
class LinkBotParticipantCommandHandler(BaseCommandHandler[LinkBotParticipantCommand, LinkBotParticipantResponseDTO]): # <-- Corrected return type
    """Handler for adding a participant to a bot."""

    _unit_of_work: BotUnitOfWork
    _access_service: BotAccessService
    _user_lookup_service: UserLookupService
    _mediator: Mediator
    _allowed_roles: list[str]
    _bot_participant_mapper: BotParticipantDTOMapper = field(init=False, repr=False) # Inject the mapper

    def __post_init__(self):
        # Initialize the mapper here
        self._bot_participant_mapper = BotParticipantDTOMapper(BotParticipantEntity, BotParticipantDTO)


    async def __call__(self, command: LinkBotParticipantCommand) -> LinkBotParticipantResponseDTO: # <-- Corrected return type
        """
        Handles adding a participant:
        1. Validates access permissions
        2. Finds the user to add by email
        3. Checks if the user is already a participant
        4. Creates the BotParticipantEntity
        5. Persists the new participant
        6. Returns details of the new participant record
        """
        logger.info(
            f"Attempting to add participant '{command.participant_email}' with role '{command.participant_role}' to bot '{command.bot_uid}'")

        # Find the user to be added
        participant_user_info: Optional[UserInfo] = await self._user_lookup_service.find_user_by_email(command.participant_email)
        if not participant_user_info:
            logger.warning(f"User with email '{command.participant_email}' not found.")
            raise UserNotFoundError(f"User with email '{command.participant_email}' not found.")

        # Check access to the target bot
        target_bot = await self._access_service.check_single_bot_access(
            user_uid=command.user_uid,
            bot_uid=command.bot_uid,
            allowed_roles=self._allowed_roles
        )
        # Prevent owner from being added as participant
        # Ensure comparison is consistent (UUID vs str conversion)
        if participant_user_info.uid == str(target_bot.user_uid): # Assuming target_bot.user_uid is UUID
            logger.warning(f"Attempted to add bot owner ({command.participant_email}) as a participant.")
            raise CannotAddOwnerAsParticipantError("Cannot add the bot owner as a participant.")

        async with self._unit_of_work as uow: # Use the UoW context manager
            # Check if user is already a participant
            existing_participant = await uow.bot_participant_repository.find_by_bot_and_user( # Assuming this method name
                bot_uid=target_bot.uid,
                user_uid=uuid.UUID(participant_user_info.uid) # Convert to UUID if necessary
            )
            if existing_participant:
                logger.warning(
                    f"User '{command.participant_email}' is already a participant in bot '{target_bot.uid}'.")
                raise ParticipantAlreadyExistsError( # <-- Corrected exception usage
                    f"User '{command.participant_email}' is already a participant in this bot.")

            # Create the BotParticipantEntity
            new_participant_entity = BotParticipantEntity(
                uid=uuid.uuid4(),
                bot_uid=target_bot.uid,
                user_uid=uuid.UUID(participant_user_info.uid), # Convert to UUID if necessary
                role=command.participant_role
            )
            logger.debug(f"Creating new BotParticipantEntity for user {participant_user_info.uid}")

            # Persist the new participant
            created_participant = await uow.bot_participant_repository.create(new_participant_entity)
            # UoW commit is implicitly called on exiting `async with uow:` block if no exception

        logger.info(
            f"Successfully added participant '{command.participant_email}' (UID: {participant_user_info.uid}) to bot '{target_bot.uid}' with role '{command.participant_role}'.")

        # Use the mapper to create the BotParticipantDTO, enriching it with user info
        participant_dto = self._bot_participant_mapper.to_dto(created_participant, participant_user_info)

        # Return the LinkBotParticipantResponseDTO
        return LinkBotParticipantResponseDTO(
            message=f"User {participant_user_info.email} successfully linked as '{command.participant_role}' to bot.",
            participant=participant_dto
        )