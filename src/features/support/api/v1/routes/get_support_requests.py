# src/features/support/api/routers/get_support_requests_router.py
# Or integrate into your existing support router file

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.core.mediator.mediator import Mediator
from src.features.identity.dependencies import get_current_user  # Assuming your authentication dependency
from src.features.identity.domain.entities.user_entity import UserEntity
from src.features.identity.exceptions.user_exceptions import UserNotFoundError
from src.features.support.api.v1.dtos.get_support_dto import SupportDTO  # Your response DTO for a single support request
from src.features.support.application.queries.get_supports.get_supports_query import GetSupportsQuery
from src.features.support.domain.value_objects.support_enums import SupportCategory  # Your enum for categories



get_supports_router = APIRouter()


@get_supports_router.get(
    "/",
    response_model=List[SupportDTO],
    summary="Get a list of support requests for the current user",
    status_code=status.HTTP_200_OK,
)
@inject
async def get_supports(
    category: Optional[SupportCategory] = Query(
        None,
        description="Filter support requests by category (e.g., 'technical_issue', 'billing')."
    ),
    mediator: Mediator = Depends(Provide["mediator"]),
    current_user: UserEntity = Depends(get_current_user),
):
    """
    Retrieves a list of support requests submitted by the authenticated user.
    Optionally filters the requests by a specified category.
    """
    logger.info(f"Fetching support requests for user: {current_user.uid}, category filter: {category}")

    # 1. Create the query object
    query = GetSupportsQuery(
        user_uid=current_user.uid,
        category=category,
    )

    # 2. Execute the query via the mediator
    try:
        supports = await mediator.query(query)
        logger.info(f"Successfully retrieved {len(supports)} support requests for user {current_user.uid}.")
        return supports
    except UserNotFoundError as e:
        logger.warning(f"Attempt to fetch support requests for non-existent user UID in token: {current_user.uid}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        ) from e
    except Exception as e:
        logger.critical(
            f"Unhandled exception fetching support requests for user {current_user.uid}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving your support requests."
        ) from e

