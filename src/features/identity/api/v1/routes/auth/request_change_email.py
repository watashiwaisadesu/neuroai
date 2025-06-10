# src/features/identity/api/routers/change_email_request_router.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException, status

from src.core.mediator.mediator import Mediator
from src.features.identity.api.v1.dtos.auth.change_email_dto import (
    RequestChangeEmailRequestDTO,
    RequestChangeEmailResponseDTO
)
from src.features.identity.application.commands.auth.request_change_email.change_email_command import RequestChangeEmailCommand
from src.features.identity.dependencies import get_role_checker, get_current_user
from src.features.identity.domain.entities.user_entity import UserEntity
from src.features.identity.exceptions.auth_exceptions import EmailAlreadyInUseError



request_change_email_router = APIRouter()


@request_change_email_router.post(
    "/request/email/change",
    response_model=RequestChangeEmailResponseDTO,
    dependencies=[Depends(get_role_checker(["user", "admin"]))]
)
@inject
async def request_change_email(
        email_data: RequestChangeEmailRequestDTO,
        current_user: UserEntity = Depends(get_current_user),
        mediator: Mediator = Depends(Provide["mediator"]),
):
    """
    Request email change - generates token and triggers email notification via event
    """
    try:
        # Create change email command
        command = RequestChangeEmailCommand(
            user_uid=current_user.uid,
            new_email=email_data.new_email
        )

        # Execute command through mediator
        response: RequestChangeEmailResponseDTO = await mediator.execute(command)

        return response

    except EmailAlreadyInUseError as e:
        logger.warning(f"Email change request failed: {email_data.new_email} already in use")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email address is already in use."
        )
    except Exception as e:
        logger.error(f"Unexpected error during email change request for user {current_user.uid}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred during email change request."
        )