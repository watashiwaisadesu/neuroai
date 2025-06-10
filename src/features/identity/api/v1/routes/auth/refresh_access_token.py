from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status, HTTPException

from src.core.mediator.mediator import Mediator
from src.features.identity.api.v1.dtos.auth.login_user_dto import TokenResponseDTO
from src.features.identity.application.commands.auth.refresh_access_token.refresh_access_token_command import \
    RefreshTokenUserCommand
from src.features.identity.dependencies import get_refresh_token_bearer, get_role_checker
from src.features.identity.exceptions.auth_exceptions import InvalidTokenError



refresh_token_user_router = APIRouter()


@refresh_token_user_router.post(
    "/refresh-token",
    response_model=TokenResponseDTO,
    status_code=status.HTTP_200_OK
)
@inject
async def refresh_access_token(
        token_data: dict = Depends(get_refresh_token_bearer()),
        mediator: Mediator = Depends(Provide["mediator"]),
):
    """
    Refresh access token using valid refresh token
    """
    try:
        # Create refresh token command
        command = RefreshTokenUserCommand(token_data=token_data)

        # Execute command through mediator
        response: TokenResponseDTO = await mediator.execute(command)

        return response

    except InvalidTokenError as e:
        logger.warning(f"Invalid token during refresh: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred during token refresh."
        )