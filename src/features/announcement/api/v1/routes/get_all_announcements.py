# src/features/announcements/api/routes/get_all_announcements.py (or modify your existing announcement_router file)

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger

from src.core.mediator.mediator import Mediator # Ensure Mediator is correctly imported

from src.features.announcement.api.v1.dtos.announcements_response_dto import GetAnnouncementsResponseDTO  # Re-using your DTO
from src.features.announcement.application.queries.get_all_announcements.get_all_announcements_query import GetAllAnnouncementsQuery



# Assuming this is your main router for announcements
get_all_announcements_router = APIRouter()


@get_all_announcements_router.get(
    "/",
    response_model=GetAnnouncementsResponseDTO,
    summary="Retrieve all announcements",
    status_code=status.HTTP_200_OK,
)
@inject
async def get_all_announcements(
        mediator: Mediator = Depends(Provide["mediator"]),
):
    """
    Retrieves a list of all system-wide announcements.
    """
    logger.info("Received request to retrieve all announcements.")
    try:
        query = GetAllAnnouncementsQuery()
        # Execute the query via the mediator
        response = await mediator.query(query)

        return response
    except Exception as e:
        logger.error(f"Error retrieving announcements: {e}", exc_info=True)
        # You might raise a more specific HTTPException based on the error type
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve announcements."
        ) from e