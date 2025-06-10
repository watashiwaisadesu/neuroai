# src/features/identity/api/routers/reset_password_request_router.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status, HTTPException

from src.core.mediator.mediator import Mediator
from src.di_container import ApplicationContainer
from src.features.identity.api.v1.dtos.auth.reset_password_request_dto import RequestResetPasswordRequestDTO, \
    RequestResetPasswordResponseDTO
from src.features.identity.application.commands.auth.request_reset_password.reset_password_request_command import \
    RequestResetPasswordCommand



request_reset_password_router = APIRouter()


@request_reset_password_router.post(
    "/request/password/reset",
    response_model=RequestResetPasswordResponseDTO,
    status_code=status.HTTP_200_OK
)
@inject
async def request_reset_password(
        email_data: RequestResetPasswordRequestDTO,
        mediator: Mediator = Depends(Provide[ApplicationContainer.mediator]),
):
    """
    Request password reset - generates token and triggers email notification via event
    """
    try:
        # Create reset password command
        command = RequestResetPasswordCommand(email=email_data.email)

        # Execute command through mediator
        response: RequestResetPasswordResponseDTO = await mediator.execute(command)

        return response

    except Exception as e:
        logger.error(f"Unexpected error during password reset request for {email_data.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred during password reset request."
        )