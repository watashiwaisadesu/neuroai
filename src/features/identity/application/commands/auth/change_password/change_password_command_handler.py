# src/features/identity/application/commands/auth/change_password/change_password_command_handler.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass, field

from src.core.base.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.core.utils.hashing import verify_password, hash_password
from src.features.identity.api.v1.dtos.auth.change_password_dto import ChangePasswordResponseDTO
from src.features.identity.api.v1.dtos.auth.login_user_dto import MinimalUserDTO
from src.features.identity.application.commands.auth.change_password.change_password_command import \
    ChangePasswordCommand
from src.features.identity.application.mappers.minimal_user_dto_mapper import MinimalUserDTOMapper
from src.features.identity.domain.entities.user_entity import UserEntity
from src.features.identity.domain.repositories.user_unit_of_work import UserUnitOfWork
from src.features.identity.exceptions.auth_exceptions import InvalidCredentialsError, PasswordsDoNotMatchError




@dataclass
class ChangePasswordCommandHandler(BaseCommandHandler[ChangePasswordCommand, ChangePasswordResponseDTO]):
    _unit_of_work: UserUnitOfWork
    _mediator: Mediator

    _minimal_user_dto_mapper: MinimalUserDTOMapper = field(init=False, repr=False)

    def __post_init__(self):
        self._minimal_user_dto_mapper = MinimalUserDTOMapper(UserEntity, MinimalUserDTO)

    async def __call__(self, command: ChangePasswordCommand) -> ChangePasswordResponseDTO:
        """
        Handles the password change request:
        1. Verifies the current password.
        2. Checks if new passwords match.
        3. Hashes the new password.
        4. Updates the user entity within a transaction.
        5. Returns a success response.
        """
        current_user = command.current_user

        logger.info(f"Attempting password change for user UID: {current_user.uid}")

        # 1. Verify Current Password
        if not verify_password(command.current_password, current_user.password_hash):
            logger.warning(f"Invalid current password provided for user UID: {current_user.uid}")
            raise InvalidCredentialsError("Invalid current password provided.")

        # 2. Verify New Passwords Match
        if command.new_password != command.confirm_new_password:
            logger.warning(f"New password confirmation failed for user UID: {current_user.uid}")
            raise PasswordsDoNotMatchError("New passwords do not match.")

        # 3. Hash New Password
        new_hashed_password = hash_password(command.new_password)

        # 4. Update User within Unit of Work transaction
        try:
            async with self._unit_of_work as uow:
                logger.debug(f"Updating password hash for user UID: {current_user.uid}")

                # Update the entity's state
                current_user.change_password(new_hashed_password)

                # Update in repository
                updated_user: UserEntity = await uow.user_repository.update(current_user)

                logger.info(f"Password successfully changed for user UID: {current_user.uid}")

                # Publish domain events if any
                events_to_publish = updated_user.pull_events()
                if events_to_publish:
                    await self._mediator.publish(events_to_publish)

        except Exception as e:
            logger.error(f"Failed to update password in database for user UID {current_user.uid}: {e}", exc_info=True)
            raise RuntimeError("Failed to update password due to a server error.") from e

        # 5. Return Success Response
        logger.debug(f"Password change successful, preparing response for user UID: {current_user.uid}")

        user_dto = self._minimal_user_dto_mapper.to_dto(updated_user)

        return ChangePasswordResponseDTO(
            message="Password changed successfully.",
            user=MinimalUserDTO(**user_dto.model_dump())
        )