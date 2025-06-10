# src/features/identity/api/routers/callback_google_oauth_router.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException, status

from src.core.mediator.mediator import Mediator
from src.features.identity.api.v1.dtos.auth.login_user_dto import TokenResponseDTO
from src.features.identity.application.commands.auth.callback_google_oauth.callback_google_oauth_command import \
    CallbackGoogleOauthCommand
from src.features.identity.exceptions.auth_exceptions import (
    GoogleTokenExchangeError,
    GoogleUserInfoFetchError,
    OAuthUserCreationError,
)



callback_google_oauth_router = APIRouter()


@callback_google_oauth_router.post(
    "/oauth/google/callback",
    response_model=TokenResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def callback_google_oauth(
        code: str,
        mediator: Mediator = Depends(Provide["mediator"]),
):
    """
    Handle Google OAuth callback - processes authorization code and returns tokens
    """
    try:
        # Create Google OAuth callback command
        command = CallbackGoogleOauthCommand(code=code)

        # Execute command through mediator
        response: TokenResponseDTO = await mediator.execute(command)

        return response

    except GoogleTokenExchangeError as e:
        logger.warning(f"Google token exchange failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange authorization code for access token."
        )
    except GoogleUserInfoFetchError as e:
        logger.warning(f"Failed to fetch Google user info: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to retrieve user information from Google."
        )
    except OAuthUserCreationError as e:
        logger.error(f"OAuth user creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account during OAuth flow."
        )
    except Exception as e:
        logger.error(f"Unexpected error during Google OAuth callback: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred during OAuth authentication."
        )