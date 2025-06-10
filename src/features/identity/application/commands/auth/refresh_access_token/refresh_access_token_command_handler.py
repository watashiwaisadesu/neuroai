# src/features/identity/application/commands/auth/refresh_access_token/refresh_access_token_command_handler.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass
from datetime import datetime, timezone

from src.core.base.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.features.identity.api.v1.dtos.auth.login_user_dto import TokenResponseDTO, TokenDTO, MinimalUserDTO
from src.features.identity.application.commands.auth.refresh_access_token.refresh_access_token_command import \
    RefreshTokenUserCommand
from src.features.identity.application.services.token_blocklist_service import TokenBlocklistService
from src.features.identity.application.services.token_service import TokenService
from src.features.identity.domain.repositories.user_unit_of_work import UserUnitOfWork
from src.features.identity.exceptions.auth_exceptions import InvalidTokenError




@dataclass
class RefreshAccessTokenCommandHandler(BaseCommandHandler[RefreshTokenUserCommand, TokenResponseDTO]):
    _unit_of_work: UserUnitOfWork
    _token_service: TokenService
    _blocklist_service: TokenBlocklistService
    _mediator: Mediator

    async def __call__(self, command: RefreshTokenUserCommand) -> TokenResponseDTO:
        """
        Handle refresh token request - EXACT same logic as your original implementation
        """
        token_data = command.token_data

        exp_timestamp = token_data.get("exp")
        platform_user_payload = token_data.get("user")  # Assuming user data is nested
        jti = token_data.get("jti")

        expiry_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        if expiry_datetime <= datetime.now(timezone.utc):
            logger.info(f"Refresh token expired (JTI: {jti}).")
            raise InvalidTokenError("Refresh token has expired")

        if await self._blocklist_service.is_blocked(jti):
            logger.warning(f"Attempted reuse of already blocklisted refresh token (JTI: {jti}).")
            raise InvalidTokenError("Refresh token has already been used or revoked.")

        try:
            await self._blocklist_service.block_token(jti, expiry=exp_timestamp)
            logger.info(f"Blocklisted used refresh token (JTI: {jti}).")
        except Exception as e:
            logger.error(f"Failed to blocklist refresh token JTI {jti}: {e}", exc_info=True)
            raise  # Re-raise

        user_uid = platform_user_payload.get("user_uid")
        if not user_uid:
            raise InvalidTokenError("Missing user_uid in token payload.")

        new_access_token = self._token_service.create_access_token({
            "email": platform_user_payload.get("email"),
            "user_uid": str(platform_user_payload.get("user_uid")),
            "role": platform_user_payload.get("role"),
        })

        new_refresh_token = self._token_service.create_refresh_token({
            "email": platform_user_payload.get("email"),
            "user_uid": str(platform_user_payload.get("user_uid")),
            "role": platform_user_payload.get("role"),
        })

        logger.info(f"Issued new access/refresh tokens for user UID: {user_uid} (Old JTI: {jti}).")

        return TokenResponseDTO(
            message="Tokens refreshed successfully.",
            tokens=TokenDTO(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
            ),
            user=MinimalUserDTO(
                email=platform_user_payload.get("email"),
                uid=platform_user_payload.get("user_uid"),
                role=platform_user_payload.get("role"),
            )
        )