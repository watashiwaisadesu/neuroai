# src/features/bot/application/commands/bot_management/transfer_bot/transfer_bot_command_handler.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
import uuid
from dataclasses import dataclass

from src.core.mediator.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.features.bot.api.v1.dtos.get_user_bots_dto import BotResponseDTO
from src.features.bot.application.commands.bot_management.transfer_bot.transfer_bot_command import TransferBotCommand
from src.features.bot.application.services.bot_access_service import BotAccessService
from src.features.bot.application.services.user_lookup_service import UserLookupService
from src.features.bot.domain.entities.bot_participant_entity import BotParticipantEntity
from src.features.bot.domain.enums import OWNER_ROLE_VALUE
from src.features.bot.domain.repositories.bot_unit_of_work import BotUnitOfWork
from src.features.bot.exceptions.bot_exceptions import (
    CannotTransferToSelfError,
    NewOwnerNotFoundError
)
from src.features.bot.utils import build_bot_response




@dataclass
class TransferBotCommandHandler(BaseCommandHandler[TransferBotCommand, BotResponseDTO]):
    _unit_of_work: BotUnitOfWork
    _mediator: Mediator
    _access_service: BotAccessService
    _user_lookup_service: UserLookupService
    _allowed_roles: list[str]

    async def __call__(self, command: TransferBotCommand) -> BotResponseDTO:
        """Handles the bot transfer request with access control."""
        logger.info(f"Initiating transfer of bot {command.bot_uid} to new owner email '{command.new_owner_email}'.")

        # Find the new owner by email
        new_owner = await self._user_lookup_service.find_user_by_email(command.new_owner_email)
        if not new_owner:
            logger.warning(f"Transfer failed: New owner with email '{command.new_owner_email}' not found.")
            raise NewOwnerNotFoundError(
                f"User with email '{command.new_owner_email}' not found to transfer ownership to.")

        logger.info(f"New owner found: {new_owner.uid} ({new_owner.email})")

        bot_to_transfer = await self._access_service.check_single_bot_access(
            user_uid=command.user_uid,
            bot_uid=command.bot_uid,
            allowed_roles=self._allowed_roles
        )
        logger.info(f"Duplicating bot {bot_to_transfer.uid} for user {command.user_uid}")

        async with self._unit_of_work:
            old_owner_uid = bot_to_transfer.user_uid
            # Check if transferring to self
            if str(old_owner_uid) == str(new_owner.uid):
                logger.warning(f"Transfer failed: Attempt to transfer bot {bot_to_transfer.uid} to its current owner.")
                raise CannotTransferToSelfError("Cannot transfer bot ownership to the current owner.")

            # 1. Change ownership on the BotEntity
            bot_to_transfer.transfer_ownership(uuid.UUID(new_owner.uid))
            updated_bot = await self._unit_of_work.bot_repository.update(bot_to_transfer)
            logger.info(f"Bot {bot_to_transfer.uid} ownership updated to {new_owner.uid} in DB.")


            # 2. Remove old owner's owner participant record
            logger.debug(f"Checking old owner participant record for user {old_owner_uid}, bot {bot_to_transfer.uid}")
            old_owner_participant = await self._unit_of_work.bot_participant_repository.find_by_bot_and_user(
                bot_uid=bot_to_transfer.uid,
                user_uid=old_owner_uid
            )

            if old_owner_participant and old_owner_participant.role == OWNER_ROLE_VALUE:
                await self._unit_of_work.bot_participant_repository.delete_by_uid(
                    bot_to_transfer.uid,
                    old_owner_participant.user_uid
                )
                logger.info(f"Removed old owner's 'owner' participant record for bot {bot_to_transfer.uid}.")

            # 3. Create or update new owner's participant record
            logger.debug(f"Ensuring new owner participant record for user {new_owner.uid}, bot {bot_to_transfer.uid}")
            new_owner_existing_participant = await self._unit_of_work.bot_participant_repository.find_by_bot_and_user(
                bot_uid=bot_to_transfer.uid,
                user_uid=uuid.UUID(str(new_owner.uid))
            )

            if new_owner_existing_participant:
                if new_owner_existing_participant.role != OWNER_ROLE_VALUE:
                    new_owner_existing_participant.change_role(OWNER_ROLE_VALUE)
                    await self._unit_of_work.bot_participant_repository.update(new_owner_existing_participant)
                    logger.info(f"Updated existing participant {new_owner.uid} to '{OWNER_ROLE_VALUE}' role.")
            else:
                new_owner_participant = BotParticipantEntity(
                    uid=uuid.uuid4(),
                    bot_uid=bot_to_transfer.uid,
                    user_uid=uuid.UUID(str(new_owner.uid)),
                    role=OWNER_ROLE_VALUE
                )
                await self._unit_of_work.bot_participant_repository.create(new_owner_participant)
                logger.info(f"Added new owner {new_owner.uid} as '{OWNER_ROLE_VALUE}' participant.")


        logger.info(f"Bot {bot_to_transfer.uid} successfully transferred to {new_owner.email}.")

        # Build response
        bot_response = await build_bot_response(
            bot=updated_bot,
            bot_uow=self._unit_of_work,
            user_lookup_service=self._user_lookup_service,
        )

        return BotResponseDTO(message="Bot transfer successful!",bot=bot_response)