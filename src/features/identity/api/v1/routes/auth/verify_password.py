# src/features/identity/api/routers/reset_password_confirm_router.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status, HTTPException

from src.core.mediator.mediator import Mediator
from src.features.identity.api.v1.dtos.auth.reset_password_confirm_dto import (
    VerifyResetPasswordRequestDTO,
    ResetPasswordConfirmResponseDTO
)
from src.features.identity.application.commands.auth.verify_password.verify_password_command import \
    VerifyPasswordCommand
from src.features.identity.exceptions.auth_exceptions import PasswordsDoNotMatchError, InvalidTokenError
from src.features.identity.exceptions.user_exceptions import UserNotFoundError



verify_reset_password_router = APIRouter()


@verify_reset_password_router.patch(
    "/verify/password/{token}",
    response_model=ResetPasswordConfirmResponseDTO,
    status_code=status.HTTP_200_OK,
)
@inject
async def verify_reset_password(
        token: str,
        dto: VerifyResetPasswordRequestDTO,
        mediator: Mediator = Depends(Provide["mediator"]),
):
    """
    Verify and confirm password reset using token
    """
    try:
        # Create verify reset password command
        command = VerifyPasswordCommand(token=token, data=dto)

        # Execute command through mediator
        response: ResetPasswordConfirmResponseDTO = await mediator.execute(command)

        return response

    except PasswordsDoNotMatchError as e:
        logger.warning(f"Password confirmation failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match.")
    except InvalidTokenError as e:
        logger.warning(f"Invalid token during password reset: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except UserNotFoundError as e:
        logger.warning(f"User not found during password reset: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        logger.error(f"Runtime error during password reset: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during password reset verification: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred during password reset verification."
        )