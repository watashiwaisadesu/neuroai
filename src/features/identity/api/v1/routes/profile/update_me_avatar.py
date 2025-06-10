# 5. Router (src/features/identity/api/routes/profile/update_avatar_router.py)
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status

from src.core.mediator.mediator import Mediator
from src.features.identity.api.v1.dtos.profile.update_avatar_dto import AvatarUploadResponseDTO
from src.features.identity.application.commands.profile.update_avatar.update_avatar_command import UpdateAvatarCommand
from src.features.identity.dependencies import get_current_user, get_role_checker

update_avatar_router = APIRouter()


@update_avatar_router.patch(
    "/me/avatar",
    response_model=AvatarUploadResponseDTO,
    dependencies=[Depends(get_role_checker(["user", "admin"]))]

)
@inject
async def update_user_avatar(
        avatar_file: UploadFile = File(...),
        current_user=Depends(get_current_user),
        mediator: Mediator = Depends(Provide["mediator"]),
):
    # Validate file type (optional but recommended)
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if avatar_file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )

    # Validate file size (optional but recommended)
    max_size = 5 * 1024 * 1024  # 5MB
    if hasattr(avatar_file, 'size') and avatar_file.size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {max_size / 1024 / 1024}MB"
        )

    if not avatar_file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file uploaded.")

    file_contents = await avatar_file.read()
    filename = avatar_file.filename
    content_type = avatar_file.content_type
    await avatar_file.close() # Explicitly close the file after reading

    # Create command
    command = UpdateAvatarCommand(
        user_uid=str(current_user.uid),
        avatar_file_data=file_contents,
        filename=filename,
        content_type=content_type
    )

    # Execute via mediator
    return await mediator.execute(command)