# src/features/identity/api/routers/logout_router.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Security, status, HTTPException

from src.core.mediator.mediator import Mediator
from src.features.identity.api.v1.dtos.auth.logout_user_dto import LogoutUserResponseDTO
from src.features.identity.application.commands.auth.logout.logout_user_command import LogoutUserCommand
from src.features.identity.dependencies import get_access_token_bearer, get_role_checker



logout_user_router = APIRouter()


@logout_user_router.post(
    "/logout",
    response_model=LogoutUserResponseDTO,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_role_checker(["user", "admin"]))]
)
@inject
async def logout_user(
        token_data: dict = Security(get_access_token_bearer()),
        mediator: Mediator = Depends(Provide["mediator"]),
):
    """
    Logout user by blocklisting their token and publishing logout event
    """
    try:
        # Create logout command
        command = LogoutUserCommand(token_data=token_data)

        # Execute command through mediator
        response: LogoutUserResponseDTO = await mediator.execute(command)

        return response

    except ValueError as e:
        logger.warning(f"Logout validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except TypeError as e:
        logger.warning(f"Logout token structure error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during logout: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred during logout."
        )