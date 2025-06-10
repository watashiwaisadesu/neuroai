# src/features/identity/application/commands/auth/callback_google_oauth/callback_google_oauth_command_handler.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass, field

from src.core.base.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.features.identity.api.v1.dtos.auth.login_user_dto import TokenResponseDTO, TokenDTO, MinimalUserDTO
from src.features.identity.application.commands.auth.callback_google_oauth.callback_google_oauth_command import \
    CallbackGoogleOauthCommand
from src.features.identity.application.mappers.minimal_user_dto_mapper import MinimalUserDTOMapper
from src.features.identity.application.services.oauth_client_service import OAuthClientService
from src.features.identity.application.services.token_service import TokenService
from src.features.identity.domain.entities.user_entity import UserEntity
from src.features.identity.domain.events.oauth_events import OAuthLoginSuccessfulEvent
from src.features.identity.domain.repositories.user_unit_of_work import UserUnitOfWork
from src.features.identity.exceptions.auth_exceptions import (
    GoogleTokenExchangeError,
    GoogleUserInfoFetchError,
    OAuthUserCreationError,
)




@dataclass
class CallbackGoogleOauthCommandHandler(BaseCommandHandler[CallbackGoogleOauthCommand, TokenResponseDTO]):
    _unit_of_work: UserUnitOfWork
    _oauth_client_service: OAuthClientService
    _token_service: TokenService
    _mediator: Mediator

    _minimal_user_dto_mapper: MinimalUserDTOMapper = field(init=False, repr=False)

    def __post_init__(self):
        self._minimal_user_dto_mapper = MinimalUserDTOMapper(UserEntity, MinimalUserDTO)

    async def __call__(self, command: CallbackGoogleOauthCommand) -> TokenResponseDTO:
        """
        Handle Google OAuth callback - EXACT same logic as your original implementation
        """
        logger.debug(f"[OAuth] Received raw code: {command.code}")

        # 1. Exchange code for token - same logic as original
        try:
            token = await self._oauth_client_service.exchange_code_for_token(command.code)
        except Exception:
            logger.exception("Token exchange failed")
            raise GoogleTokenExchangeError()

        # 2. Fetch user info from Google - same logic as original
        try:
            name, email = await self._oauth_client_service.fetch_user_info(token)
        except Exception:
            logger.exception("Failed to fetch user info from Google")
            raise GoogleUserInfoFetchError()

        async with self._unit_of_work as uow:  # ✅ Start transaction
            # Check if user exists
            user = await uow.user_repository.find_by_email(email)
            is_new_user = user is None

            if not user:
                try:
                    user_entity = UserEntity.register_oauth(
                        email=email,
                    )
                    # Create user within transaction
                    user = await uow.user_repository.create(user_entity)

                    logger.info(f"Created new OAuth user: {user.uid} ({email})")

                    events_to_publish = user_entity.pull_events()
                    if events_to_publish:
                        await self._mediator.publish(events_to_publish)

                except Exception:
                    logger.exception("User creation failed during OAuth flow")
                    raise OAuthUserCreationError()

        # 5. Generate tokens - same logic as original
        access_token = self._token_service.create_access_token({
            "email": user.email,
            "user_uid": str(user.uid),
            "role": user.role
        })

        refresh_token = self._token_service.create_refresh_token({
            "email": user.email,
            "user_uid": str(user.uid),
            "role": user.role
        })

        if is_new_user:
            response_message = "New user created and logged in successfully."
        else:
            response_message = "User logged in successfully."

        user_dto = self._minimal_user_dto_mapper.to_dto(user)
        # 6. Publish login successful event
        login_event = OAuthLoginSuccessfulEvent(
            user_uid=user.uid,
            email=user.email,
            provider="google",
            is_new_user=is_new_user
        )
        await self._mediator.publish([login_event])

        logger.info(f"OAuth login successful for user {user.uid} (new_user: {is_new_user})")

        return TokenResponseDTO(
            message=response_message,
            tokens=TokenDTO(
                access_token=access_token,
                refresh_token=refresh_token,
            ),
            user=MinimalUserDTO(**user_dto.model_dump())
        )