from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from src.core.mediator.mediator import Mediator
from src.features.identity.api.v1.dtos.profile.get_me_dto import UserResponseDTO
from src.features.identity.application.queries.profile.get_me.get_me_query import GetMeQuery
from src.features.identity.dependencies import get_current_user, get_role_checker

get_me_router = APIRouter()


@get_me_router.get(
    "/me",
    response_model=UserResponseDTO,
    dependencies=[Depends(get_role_checker(["user", "admin"]))],
    responses={
        200: {
            "description": "User profile retrieved successfully",
            "model": UserResponseDTO
        }
    }
)
@inject
async def get_me(
        current_user=Depends(get_current_user),
        mediator: Mediator = Depends(Provide["mediator"]),
):
    """Get current user's profile information"""
    # Create query
    query = GetMeQuery(user_uid=str(current_user.uid))

    # Execute via mediator
    return await mediator.query(query)