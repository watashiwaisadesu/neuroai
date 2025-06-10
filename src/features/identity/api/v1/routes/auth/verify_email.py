# src/features/identity/api/routers/verify_email_router.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger

from dependency_injector.wiring import inject, Provide
from fastapi import Depends, APIRouter, HTTPException, status

from src.core.mediator.mediator import Mediator
from src.features.identity.api.v1.dtos.auth.verify_email_dto import VerifyEmailResponseDTO
from src.features.identity.application.commands.auth.verify_email.verify_email_command import VerifyEmailCommand
from src.features.identity.exceptions.auth_exceptions import (
    InvalidEmailVerificationToken,
    TokenMissingData,
    UserNotFoundForToken
)



verify_email_router = APIRouter()


@verify_email_router.patch(
    "/verify/email/{token}",
    response_model=VerifyEmailResponseDTO
)
@inject
async def verify_email(
        token: str,
        mediator: Mediator = Depends(Provide["mediator"]),
):
    """
    Verify email change using token
    """
    try:
        # Create verify email command
        command = VerifyEmailCommand(token=token)

        # Execute command through mediator
        user_response: VerifyEmailResponseDTO = await mediator.execute(command)

        return user_response.model_dump()

    except InvalidEmailVerificationToken as e:
        logger.warning(f"Invalid email verification token: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired email verification token."
        )
    except TokenMissingData as e:
        logger.warning(f"Token missing data: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token format."
        )
    except UserNotFoundForToken as e:
        logger.warning(f"User not found for token: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found for this verification token."
        )
    except RuntimeError as e:
        logger.error(f"Runtime error during email verification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during email verification: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred during email verification."
        )