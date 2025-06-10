# src/features/announcements/api/routes/announcements_routes.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status, HTTPException

# Adjust imports based on your project structure
from src.core.mediator.mediator import Mediator
from src.features.announcement.api.v1.dtos.create_announcement_request_dto import CreateAnnouncementRequestDTO
from src.features.announcement.api.v1.dtos.announcements_response_dto import AnnouncementResponseDTO
from src.features.announcement.application.commands.create_announcement.create_announcement_command import \
    CreateAnnouncementCommand
from src.features.identity.dependencies import get_role_checker


create_announcement_router = APIRouter()


@create_announcement_router.post(
    "/",
    response_model=AnnouncementResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_role_checker(["user", "admin"]))],
    summary="Create a new system announcement.",
    description="Allows administrators to post new platform-wide news or updates. "
                "The announcement will be created with the specified title, version, text, type, and status."
)
@inject
async def create_announcement(
    request: CreateAnnouncementRequestDTO,
    mediator: Mediator = Depends(Provide["mediator"]),
):
    """
    Handles the request to create a new announcement by sending a command to the mediator.
    """
    try:
        # Create the command from the request DTO and current_user info
        command = CreateAnnouncementCommand(
            title=request.title,
            version=request.version,
            text=request.text,
            type=request.type,
        )
        # Execute the command via the mediator
        response = await mediator.execute(command)
        return response
    except Exception as e:
        logger.exception(f"Failed to create announcement: {e}")
        # Return an appropriate HTTP error response
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create announcement due to an internal error.")