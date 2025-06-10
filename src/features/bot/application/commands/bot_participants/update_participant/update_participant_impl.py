# src/features/bot/application/commands/bot_participants/update_participant/update_participant_command_handler.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass, field  # Import 'field' for mapper injection
from typing import Optional  # Import Optional

from src.core.mediator.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
# Import the updated response DTO and BotParticipantDTO
from src.features.bot.api.v1.dtos.update_participant_dto import UpdateBotParticipantRoleResponseDTO, BotParticipantDTO
from src.features.bot.application.commands.bot_participants.update_participant.update_participant_command import \
    UpdateBotParticipantRoleCommand
from src.features.bot.application.mappers.bot_participant_dto_mapper import \
    BotParticipantDTOMapper  # Import your mapper
from src.features.bot.application.services.bot_access_service import BotAccessService
from src.features.bot.application.services.user_lookup_service import UserLookupService, \
    UserInfo  # Import UserLookupService and UserInfo
from src.features.bot.domain.entities.bot_participant_entity import \
    BotParticipantEntity  # Import BotParticipantEntity for mapper init
from src.features.bot.domain.enums import OWNER_ROLE_VALUE
from src.features.bot.domain.repositories.bot_unit_of_work import BotUnitOfWork
from src.features.bot.exceptions.bot_exceptions import (
    ParticipantNotFoundError,
    CannotUpdateOwnerRoleError
)




@dataclass
class UpdateBotParticipantRoleCommandHandler(
    BaseCommandHandler[UpdateBotParticipantRoleCommand, UpdateBotParticipantRoleResponseDTO]): # Corrected return type
    """Handler for updating a participant's role in a bot."""

    _unit_of_work: BotUnitOfWork
    _access_service: BotAccessService
    _user_lookup_service: UserLookupService # Inject UserLookupService
    _mediator: Mediator
    _allowed_roles: list[str]
    _bot_participant_mapper: BotParticipantDTOMapper = field(init=False, repr=False) # Inject the mapper

    def __post_init__(self):
        # Initialize the mapper here
        self._bot_participant_mapper = BotParticipantDTOMapper(BotParticipantEntity, BotParticipantDTO)


    async def __call__(self, command: UpdateBotParticipantRoleCommand) -> UpdateBotParticipantRoleResponseDTO:
        """
        Handles updating a participant's role:
        1. Validates access permissions
        2. Finds the participant user's info
        3. Finds the participant record
        4. Checks if trying to modify the owner
        5. Updates the participant entity's role
        6. Persists the change
        7. Returns details of the updated participant
        """
        new_role_value = command.new_role.value
        logger.info(
            f"Attempting to update role for participant user '{command.participant_user_uid}' in bot '{command.bot_uid}' to '{new_role_value}'")

        # 1. Check access to the target bot
        target_bot = await self._access_service.check_single_bot_access(
            user_uid=command.current_user_uid,
            bot_uid=command.bot_uid,
            allowed_roles=self._allowed_roles,
        )

        # 2. Get the participant user's info for DTO enrichment
        participant_user_info: Optional[UserInfo] = await self._user_lookup_service.get_user_by_uid(str(command.participant_user_uid))
        if not participant_user_info:
            logger.warning(f"Participant user {command.participant_user_uid} not found in user lookup service.")
            # This case might indicate a data inconsistency or deleted user, but we proceed to find the participant entity
            # A more robust system might raise UserNotFoundError here if the participant MUST exist in identity service.
            # For now, we'll allow it and just won't have email/avatar.

        # 3. Prevent changing role for the bot owner
        if command.participant_user_uid == target_bot.user_uid:
            logger.warning(
                f"Attempt denied: Trying to change role for owner (User UID: {command.participant_user_uid}) of bot {command.bot_uid}.")
            raise CannotUpdateOwnerRoleError("Cannot change the bot owner's role.")

        async with self._unit_of_work as uow:
            # 4. Find the existing participant
            participant_entity = await uow.bot_participant_repository.find_by_bot_and_user( # Assuming method name is find_by_bot_and_user_uid
                bot_uid=command.bot_uid,
                user_uid=command.participant_user_uid
            )

            if not participant_entity:
                logger.warning(f"Participant user {command.participant_user_uid} not found in bot {command.bot_uid}.")
                raise ParticipantNotFoundError(f"User {command.participant_user_uid} is not a participant in this bot.")

            # 5. Check if the role is actually changing
            if participant_entity.role == new_role_value:
                logger.info(
                    f"Participant {command.participant_user_uid} already has role '{new_role_value}'. No update needed.")
                # Return the current state using the mapper
                updated_participant_dto = self._bot_participant_mapper.to_dto(participant_entity, participant_user_info)
                return UpdateBotParticipantRoleResponseDTO(
                    message=f"Participant role for {participant_user_info.email if participant_user_info else command.participant_user_uid} is already '{new_role_value}'.",
                    participant=updated_participant_dto
                )
            else:
                # 6. Prevent changing from owner role (additional safeguard)
                if participant_entity.role == OWNER_ROLE_VALUE:
                    logger.warning(f"Attempt to change role from owner for user {command.participant_user_uid}")
                    raise CannotUpdateOwnerRoleError("Cannot change role from owner.")

                logger.debug(f"Changing role from '{participant_entity.role}' to '{new_role_value}'")

                # 7. Update the role using domain method
                participant_entity.change_role(new_role_value)

                # 8. Persist the updated entity
                await uow.bot_participant_repository.update(participant_entity)

        logger.info(f"Successfully updated role for participant user {command.participant_user_uid} to '{new_role_value}'.")

        # 9. Return response DTO using the mapper
        updated_participant_dto = self._bot_participant_mapper.to_dto(participant_entity, participant_user_info)
        return UpdateBotParticipantRoleResponseDTO(
            message=f"Participant role for {participant_user_info.email if participant_user_info else command.participant_user_uid} updated successfully to '{new_role_value}'.",
            participant=updated_participant_dto
        )