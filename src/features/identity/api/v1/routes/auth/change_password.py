# src/features/identity/api/routers/change_password_router.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status, HTTPException

from src.core.mediator.mediator import Mediator
from src.features.identity.api.v1.dtos.auth.change_password_dto import ChangePasswordDTO, ChangePasswordResponseDTO
from src.features.identity.application.commands.auth.change_password.change_password_command import \
    ChangePasswordCommand
from src.features.identity.dependencies import get_role_checker, get_current_user
from src.features.identity.domain.entities.user_entity import UserEntity
from src.features.identity.exceptions.auth_exceptions import InvalidCredentialsError, PasswordsDoNotMatchError



change_password_router = APIRouter()


@change_password_router.patch(
    "/change-password",
    response_model=ChangePasswordResponseDTO,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_role_checker(["user", "admin"]))]
)
@inject
async def change_password(
        password_data: ChangePasswordDTO,
        current_user: UserEntity = Depends(get_current_user),
        mediator: Mediator = Depends(Provide["mediator"]),
):
    """
    Change user password - Requires authentication and role check
    """
    try:
        # Create change password command
        command = ChangePasswordCommand(
            current_password=password_data.current_password,
            new_password=password_data.new_password,
            confirm_new_password=password_data.confirm_new_password,
            current_user=current_user
        )

        # Execute command through mediator
        response: ChangePasswordResponseDTO = await mediator.execute(command)

        return response

    except InvalidCredentialsError as e:
        logger.warning(f"Invalid credentials during password change for user {current_user.uid}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PasswordsDoNotMatchError as e:
        logger.warning(f"Password confirmation failed for user {current_user.uid}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        logger.error(f"Server error during password change for user {current_user.uid}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during password change for user {current_user.uid}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred during password change."
        )