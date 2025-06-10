# 4. Router (src/features/identity/api/routers/profile/update_me_router.py)
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Body, HTTPException

from src.core.mediator.mediator import Mediator
from src.features.identity.api.v1.dtos.profile.get_me_dto import UserResponseDTO
from src.features.identity.api.v1.dtos.profile.update_user_dto import UserUpdateRequestDTO
from src.features.identity.application.commands.profile.update_me.update_me_command import UpdateMeCommand
from src.features.identity.dependencies import get_current_user, get_role_checker

update_me_router = APIRouter()


@update_me_router.patch(
    "/me",
    response_model=UserResponseDTO,
    dependencies=[Depends(get_role_checker(["user", "admin"]))]
)
@inject
async def update_me(
        user_data: UserUpdateRequestDTO = Body(...),
        current_user=Depends(get_current_user),  # This returns the current user entity
        mediator: Mediator = Depends(Provide["mediator"]),
):
    # Convert DTO to dict and remove empty values
    update_dict = user_data.model_dump(exclude_unset=True)
    update_dict = {k: v for k, v in update_dict.items() if v not in (None, "")}

    if not update_dict:
        raise HTTPException(status_code=400, detail="User data cannot be empty")

    # Create command
    command = UpdateMeCommand(
        user_uid=str(current_user.uid),
        update_data=update_dict
    )

    # Execute via mediator
    return await mediator.execute(command)