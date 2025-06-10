# src/features/identity/application/commands/auth/logout/logout_user_command_handler.py
from src.features.identity.api.v1.dtos.auth.login_user_dto import MinimalUserDTO
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass

from src.core.base.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
# from src.features.identity.api.v1.dtos.auth.login_user_dto import MinimalUserDTO
from src.features.identity.api.v1.dtos.auth.logout_user_dto import LogoutUserResponseDTO
from src.features.identity.application.commands.auth.logout.logout_user_command import LogoutUserCommand
from src.features.identity.application.services.token_blocklist_service import TokenBlocklistService





@dataclass
class LogoutUserCommandHandler(BaseCommandHandler[LogoutUserCommand, LogoutUserResponseDTO]):
    _blocklist_service: TokenBlocklistService
    _mediator: Mediator

    async def __call__(self, command: LogoutUserCommand) -> LogoutUserResponseDTO:
        """
        Handles user logout by blocklisting the provided token's JTI.

        Args:
            command: LogoutUserCommand containing token_data

        Returns:
            A LogoutUserResponseDTO indicating success.

        Raises:
            ValueError: If the token payload is missing 'jti' or 'exp'.
            TypeError: If 'user' data within token_data is not structured as expected.
        """
        token_data = command.token_data

        # Extract token components
        user_payload = token_data.get("user")
        jti = token_data.get("jti")
        exp_timestamp = token_data.get("exp")

        # --- Input Validation ---
        if not jti:
            logger.error("Logout attempt failed: Token missing 'jti'.")
            raise ValueError("Token is missing 'jti' (token identifier)")

        if exp_timestamp is None:
            logger.error("Logout attempt failed: Token missing 'exp'.")
            raise ValueError("Token is missing 'exp' (expiration time)")

        if not user_payload or not isinstance(user_payload, dict):
            logger.error("Logout attempt failed: Invalid or missing 'user' data in token.")
            raise TypeError("Invalid or missing 'user' data structure in token payload")

        # Extract user details safely
        user_email = user_payload.get("email")
        user_uid = user_payload.get("user_uid")
        user_role = user_payload.get("role")
        if not user_email or not user_uid:
            logger.warning("Logout attempt: Token 'user' payload missing email or uid.")

        # --- Blocklist Logic ---
        try:
            await self._blocklist_service.block_token(jti, expiry=exp_timestamp)
            logger.info(f"Successfully blocklisted token JTI: {jti} for user UID: {user_uid}")

        except Exception as e:
            logger.error(f"Failed to blocklist token JTI {jti}: {e}", exc_info=True)
            raise

        # --- Construct Response ---
        return LogoutUserResponseDTO(
            message="Logged Out Successfully",
            user=MinimalUserDTO(
                email=user_email or "N/A",
                uid=user_uid or "N/A",
                role=user_role or "N/A",
            )
        )