# src/features/identity/api/routers/auth_router.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger

from dependency_injector.wiring import inject, Provide
from fastapi import Depends, HTTPException, status, APIRouter

from src.core.mediator.mediator import Mediator
from src.features.identity.api.v1.dtos.auth.register_user_dto import RegisterUserRequestDTO
from src.features.identity.api.v1.dtos.profile.get_me_dto import UserResponseDTO
from src.features.identity.application.commands.auth.register_user.register_user_command import RegisterUserCommand
from src.features.identity.exceptions.user_exceptions import UserAlreadyExistsError



register_user_router = APIRouter()


@register_user_router.post(
    "/register",
    response_model=UserResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def register_user_account(
    api_dto: RegisterUserRequestDTO,
    mediator: Mediator = Depends(Provide["mediator"]),
):
    try:
        command = RegisterUserCommand(
            email=api_dto.email,
            password=api_dto.password,
            user_type=api_dto.user_type,
            is_send_docs_to_jur_address=api_dto.is_send_docs_to_jur_address,
            phone_number=api_dto.phone_number,
            company_name=api_dto.company_name,
            field_of_activity=api_dto.field_of_activity,
            BIN=api_dto.BIN,
            legal_address=api_dto.legal_address,
            contact=api_dto.contact,
            registration_date=api_dto.registration_date
        )
        user_response: UserResponseDTO = await mediator.execute(command)
    except UserAlreadyExistsError as e:
        logger.warning(f"Registration conflict for {api_dto.email}: {e}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValueError as e:  # Catch validation errors from DTO mapping or other ValueErrors
        logger.warning(f"Validation or input error during registration: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during user registration for {api_dto.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred."
        )

    return user_response