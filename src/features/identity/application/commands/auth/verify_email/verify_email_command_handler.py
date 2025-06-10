# src/features/identity/application/commands/auth/verify_email/verify_email_command_handler.py
import json
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass, field
from uuid import UUID

from src.core.base.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.features.identity.api.v1.dtos.auth.login_user_dto import MinimalUserDTO
from src.features.identity.api.v1.dtos.auth.verify_email_dto import VerifyEmailResponseDTO
from src.features.identity.application.commands.auth.verify_email.verify_email_command import VerifyEmailCommand
from src.features.identity.application.mappers.minimal_user_dto_mapper import MinimalUserDTOMapper
from src.features.identity.domain.entities.user_entity import UserEntity
from src.features.identity.domain.repositories.user_unit_of_work import UserUnitOfWork
from src.features.identity.exceptions.auth_exceptions import (
    InvalidEmailVerificationToken,
    TokenMissingData,
    UserNotFoundForToken
)
from src.infra.services.redis.redis_service import RedisService




@dataclass
class VerifyEmailCommandHandler(BaseCommandHandler[VerifyEmailCommand, VerifyEmailResponseDTO]):
    _redis_service: RedisService
    _unit_of_work: UserUnitOfWork
    _mediator: Mediator

    _minimal_user_dto_mapper: MinimalUserDTOMapper = field(init=False, repr=False)

    def __post_init__(self):
        self._minimal_user_dto_mapper = MinimalUserDTOMapper(UserEntity, MinimalUserDTO)

    async def __call__(self, command: VerifyEmailCommand) -> VerifyEmailResponseDTO:
        """
        Handles email verification - EXACT same logic as your original implementation:
        1. Retrieves pending change data from Redis using the token.
        2. Finds the user associated with the token.
        3. Updates the user's email within a transaction.
        4. Deletes the token data from Redis.
        5. Publishes domain event for successful email change.
        6. Returns the updated user information.
        """
        key = f"pending_email_update:{command.token}"
        logger.debug(f"Attempting to verify email change with Redis key: {key}")

        # 1. Get data from Redis - same logic as original
        data = await self._redis_service.get_key(key)
        if not data:
            logger.warning(f"Invalid or expired email verification token used: {command.token}")
            raise InvalidEmailVerificationToken()

        # 2. Parse payload - same logic as original
        try:
            payload = json.loads(data)
            new_email = payload.get("new_email")
            user_uid_str = payload.get("user_uid")
            if not new_email or not user_uid_str:
                raise ValueError("Missing 'new_email' or 'user_uid' in token payload")
            user_uid = UUID(user_uid_str)
            logger.debug(f"Token payload parsed successfully for user UID: {user_uid}, new email: {new_email}")
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            logger.error(f"Failed to parse email verification token payload: {e}. Data: {data}", exc_info=True)
            raise TokenMissingData(f"Invalid token payload structure: {e}")

        # 3. Update user email within UoW transaction - same logic as original
        try:
            async with self._unit_of_work as uow:  # Use async context manager for transaction
                logger.debug(f"Finding user by UID: {user_uid}")
                user: UserEntity = await uow.user_repository.find_by_uid(user_uid)
                if not user:
                    logger.error(f"User not found for UID specified in token: {user_uid}")
                    raise UserNotFoundForToken()
                logger.debug(f"User found: {user.email}. Attempting to change email.")

                # Store old email before change
                old_email = user.email

                # --- Update Entity State - same logic as original ---
                try:
                    if user.email == new_email:
                        logger.info(f"New email is the same as current for user {user_uid}. No update needed.")
                        # Decide if this should still delete the token and return success
                    else:
                        user.change_email(new_email)
                        user.verify()
                except ValueError as e:
                    # Catch validation errors from the entity method if applicable
                    logger.warning(f"Email change validation failed for user {user_uid}: {e}")
                    raise  # Re-raise domain validation errors

                # --- Persist Changes - same logic as original ---
                updated_user = await uow.user_repository.update(user)
                # Commit is handled automatically by __aexit__

                logger.info(f"Email successfully updated for user UID: {user.uid}")

                # Publish domain events if any from the user entity
                user_events = updated_user.pull_events()
                if user_events:
                    await self._mediator.publish(user_events)

        except UserNotFoundForToken:  # Re-raise specific expected errors
            raise
        except ValueError:  # Re-raise domain validation errors
            raise
        except Exception as e:
            # Log any other exceptions during the UoW block (DB errors, etc.)
            logger.error(f"Failed to update email in database for user UID {user_uid}: {e}", exc_info=True)
            # Do NOT delete Redis key if DB update failed
            raise RuntimeError("Failed to update email due to a server error.") from e

        # 4. Delete Redis key *after* successful DB commit - same logic as original
        try:
            logger.debug(f"Deleting Redis key after successful update: {key}")
            await self._redis_service.delete_key(key)
        except Exception as e:
            # Log error but don't fail the request, as the email change succeeded
            logger.error(f"Failed to delete Redis key {key} after email verification: {e}", exc_info=True)
        # 6. Prepare and return response - same logic as original
        logger.debug(f"Preparing success response for user UID: {user.uid}")
        try:
            # Map the updated entity to the DTO for the response
            user_dto = self._minimal_user_dto_mapper.to_dto(user)
            if not user_dto:
                # Should not happen if user was found and updated
                logger.error(f"Failed to map updated user to DTO for UID: {user.uid}")
                raise RuntimeError("Failed to prepare user data for response.")

            return VerifyEmailResponseDTO(
                message="Email changed successfully.",
                user=MinimalUserDTO(**user_dto.model_dump())
            )
        except Exception as e:
            logger.error(f"Failed to map user entity to response DTO (UID: {user.uid}): {e}", exc_info=True)
            raise RuntimeError("Failed to prepare response data.")