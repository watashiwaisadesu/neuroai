from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException, status

from src.core.mediator.mediator import Mediator
from src.di_container import ApplicationContainer
from src.features.identity.api.v1.dtos.profile.get_me_dto import UserResponseDTO
from src.features.identity.application.commands.auth.verify_user.verify_user_command import VerifyUserCommand
from src.features.identity.exceptions.auth_exceptions import InvalidTokenError, AuthVerificationError
from src.features.identity.exceptions.user_exceptions import UserNotFoundError

verify_user_router = APIRouter()


@verify_user_router.patch(
    "/verify/{token}",
    response_model=UserResponseDTO,
    status_code=status.HTTP_200_OK,
)
@inject
async def verify_user_account(
    token: str,
    mediator: Mediator = Depends(Provide[ApplicationContainer.mediator]),
):
    try:
        command = VerifyUserCommand(token=token)
        user_response = await mediator.execute(command)
        return user_response
    except (InvalidTokenError, UserNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except AuthVerificationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error during account verification.",
        )
