# src/features/identity/api/routers/auth_router.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger

from dependency_injector.wiring import inject, Provide
from fastapi import Depends, HTTPException, status, APIRouter

from src.core.mediator.mediator import Mediator
from src.features.identity.api.v1.dtos.profile.get_avatar_dto import GetAvatarResponseDTO
from src.features.identity.application.queries.profile.get_avatar.get_me_avatar_query import GetMeAvatarQuery
from src.features.identity.dependencies import get_role_checker, get_current_user
from src.features.identity.domain.entities.user_entity import UserEntity  # For type hinting current_user
from src.features.identity.exceptions.user_exceptions import UserNotFoundError, AvatarNotFoundError  # New imports



get_me_avatar_router = APIRouter() # Assuming this is for general auth, not just register


@get_me_avatar_router.get(
"/me/avatar",
    response_model=GetAvatarResponseDTO,
    dependencies=[Depends(get_role_checker(["user", "admin"]))]
)
@inject
async def get_me_avatar(
    current_user: UserEntity = Depends(get_current_user),
    mediator: Mediator = Depends(Provide["mediator"]),
) -> GetAvatarResponseDTO: # Specify return type
    """
    Returns the public URL of the user's avatar.
    """
    try:
        query = GetMeAvatarQuery(user_uid=current_user.uid)
        avatar_response_dto: GetAvatarResponseDTO = await mediator.query(query)
        return avatar_response_dto
    except (UserNotFoundError, AvatarNotFoundError) as e:
        logger.warning(f"Avatar retrieval failed for user {current_user.uid}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during avatar retrieval for user {current_user.uid}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred."
        )