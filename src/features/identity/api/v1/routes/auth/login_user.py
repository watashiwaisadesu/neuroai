# src/features/identity/api/routers/auth_router.py (or a dedicated login_router.py if preferred)
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status, HTTPException

from src.core.mediator.mediator import Mediator # For type hinting
from src.features.identity.api.v1.dtos.auth.login_user_dto import LoginUserRequestDTO, TokenResponseDTO
from src.features.identity.application.commands.auth.login.login_user_command import LoginUserCommand
from src.features.identity.domain.value_objects.email_vo import Email, InvalidEmailError # Import your Email VO
from src.features.identity.exceptions.auth_exceptions import (
    AccountNotVerifiedError,
    InvalidCredentialsError
)
from src.features.identity.exceptions.user_exceptions import (
    UserNotFoundError
)



# It's common to have a single router for all auth-related endpoints,
# or separate ones if the module gets too large.
# If you consolidate, you might rename it to 'auth_router'.
login_user_router = APIRouter() # You could also use a combined 'auth_router = APIRouter()'

@login_user_router.post(
    '/login',
    response_model=TokenResponseDTO,
    status_code=status.HTTP_200_OK
)
@inject # Important for dependency_injector to wire dependencies
async def login_user_account( # Renamed for consistency with register_user_account
    api_dto: LoginUserRequestDTO,
    mediator: Mediator = Depends(Provide["mediator"]) # Inject the mediator
) -> TokenResponseDTO:

    try:
        # Create the LoginUserCommand, using your Email Value Object
        command = LoginUserCommand(
            email=api_dto.email, # Validate email through the VO constructor
            password=api_dto.password
        )
        # Execute the command via the mediator
        token_response: TokenResponseDTO = await mediator.execute(command)
        return token_response
    except InvalidEmailError as e:
        logger.warning(f"Login attempt with invalid email format: {api_dto.email} - {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except UserNotFoundError:
        logger.warning(f"Login attempt for non-existent user: {api_dto.email}")
        # Return 401 Unauthorized for security, to avoid revealing if user exists
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    except AccountNotVerifiedError:
        logger.warning(f"Login attempt for unverified account: {api_dto.email}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account not verified. Please check your email.")
    except InvalidCredentialsError:
        logger.warning(f"Login attempt with invalid password for user: {api_dto.email}")
        # Return 401 Unauthorized for security, to avoid revealing if password was only wrong
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    except Exception as e:
        logger.error(f"Unexpected error during user login for {api_dto.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred."
        )