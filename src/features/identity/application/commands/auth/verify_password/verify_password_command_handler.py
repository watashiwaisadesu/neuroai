# src/features/identity/application/commands/auth/reset_password_confirm/reset_password_confirm_command_handler.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass

from src.config import Settings
from src.core.base.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.core.utils.hashing import hash_password, decode_url_safe_token
from src.features.identity.api.v1.dtos.auth.reset_password_confirm_dto import ResetPasswordConfirmResponseDTO
from src.features.identity.application.commands.auth.verify_password.verify_password_command import VerifyPasswordCommand
from src.features.identity.domain.repositories.user_unit_of_work import UserUnitOfWork
from src.features.identity.application.services.token_blocklist_service import TokenBlocklistService
from src.features.identity.exceptions.auth_exceptions import PasswordsDoNotMatchError, InvalidTokenError
from src.features.identity.exceptions.user_exceptions import UserNotFoundError

settings: Settings = Settings()



@dataclass
class VerifyPasswordCommandHandler(BaseCommandHandler[VerifyPasswordCommand, ResetPasswordConfirmResponseDTO]):
    _unit_of_work: UserUnitOfWork
    _blocklist_service: TokenBlocklistService
    _mediator: Mediator

    async def __call__(self, command: VerifyPasswordCommand) -> ResetPasswordConfirmResponseDTO:
        """
        Validates token, checks blocklist, updates password, and blocklists token.
        EXACT same logic as your original implementation.
        """
        token_str = command.token  # The raw token string from the user
        dto = command.data  # Contains new_password and confirm_new_password

        # 1. Validate Passwords Match
        if dto.new_password != dto.confirm_new_password:
            logger.warning("Password confirmation failed: Passwords do not match.")
            raise PasswordsDoNotMatchError()

        # 2. Decode Token (Handles expiry and signature validation)
        try:
            token_payload = decode_url_safe_token(token_str)
        except ValueError as e:
            # Catch specific errors from decode function (Expired, Invalid Signature)
            logger.warning(f"Password reset token validation failed: {e}")
            raise InvalidTokenError(str(e))  # Map to your specific exception

        email = token_payload.get("email")
        nonce = token_payload.get("nonce")  # Get the nonce added during creation

        if not email or not nonce:
            logger.error(f"Invalid token payload structure: Missing email or nonce. Payload: {token_payload}")
            raise InvalidTokenError("Invalid token payload.")

        # 3. Define Blocklist Key (Using Nonce is generally safer than token hash)
        blocklist_key = f"pw_reset_nonce:{nonce}"
        # Alternative: blocklist_key = f"pw_reset_token:{hash(token_str)}"

        # 4. Check Blocklist (Prevent Replay Attack)
        is_blocked = False
        try:
            # Check if the key exists in the blocklist
            is_blocked = await self._blocklist_service.is_blocked(blocklist_key)
        except Exception as e:
            # Catch ONLY communication errors with the blocklist service
            logger.error(f"Failed to check blocklist for key {blocklist_key}: {e}", exc_info=True)
            raise RuntimeError("Could not verify token status. Please try again later.")  # Fail closed

        # Now, handle the outcome of the check *outside* the communication try/except
        if is_blocked:
            logger.warning(f"Attempted reuse of already used password reset token (Nonce: {nonce})")
            raise InvalidTokenError("Password reset link has already been used.")

        # 5. Perform Password Update within a Transaction
        try:
            async with self._unit_of_work as uow:  # Assuming UoW handles transaction context
                user = await uow.user_repository.find_by_email(email)
                if not user:
                    # Note: This case should ideally not happen if the email was validated
                    # before sending the token, but handle defensively.
                    logger.error(f"User not found for email '{email}' during password reset confirmation.")
                    raise UserNotFoundError("User not found for this password reset request.")

                # Hash the new password BEFORE setting it
                hashed_new_password = hash_password(dto.new_password)

                user.change_password(hashed_new_password)

                updated_user = await uow.user_repository.update(user)

                logger.info(f"Password successfully reset for user {email} (UID: {user.uid})")

                # Publish domain events if any
                events_to_publish = updated_user.pull_events()
                if events_to_publish:
                    await self._mediator.publish(events_to_publish)

        except Exception as e:
            # Catch DB errors or other issues during the update
            logger.error(f"Failed to update password for user {email}: {e}", exc_info=True)
            # Do NOT blocklist the token if the password change failed
            raise RuntimeError("Failed to update password. Please try again.")  # Or a more specific DB error

        # 6. Blocklist the Token *AFTER* successful password change & commit
        try:
            # Set expiry on the blocklist key to match token validity for auto-cleanup
            await self._blocklist_service.block_token(
                jti=blocklist_key,
                expiry=settings.TOKEN_RESET_TIMEOUT,
            )
            logger.info(f"Successfully blocklisted used password reset token (Nonce: {nonce})")
        except Exception as e:
            # Log failure to blocklist, but the password reset was successful.
            # This is less critical than failing the password change itself.
            logger.error(f"Failed to blocklist password reset token (Nonce: {nonce}) after successful reset: {e}", exc_info=True)
            # Don't raise an error to the user here, as their password IS reset.

        # 7. Return Success Response
        return ResetPasswordConfirmResponseDTO(message="Password reset successfully.")