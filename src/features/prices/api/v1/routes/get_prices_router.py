# src/features/prices/api/routers/price_routes.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from src.core.mediator.mediator import Mediator
from src.features.identity.dependencies import get_current_user
from src.features.identity.domain.entities.user_entity import UserEntity
from src.features.prices.api.v1.dtos.platform_prices_dto import GetPlatformsResponseDTO
from src.features.prices.application.queries.get_platform_prices_query import GetPlatformPricesQuery



get_prices_router = APIRouter()

@get_prices_router.get(
    "/",
    response_model=GetPlatformsResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get all platform prices and OpenAI price"
)
@inject
async def get_all_prices(
    mediator: Mediator = Depends(Provide["mediator"]),
    current_user: UserEntity = Depends(get_current_user), # User or Admin can view
):
    """
    Retrieves a list of all platform pricing configurations and the global OpenAI price.
    Accessible by 'user' and 'admin' roles.
    """
    query = GetPlatformPricesQuery(user_uid=current_user.uid) # Pass user for context/auditing
    try:
        response = await mediator.query(query)
        logger.info(f"All prices retrieved for user {current_user.uid}.")
        return response
    except Exception as e:
        logger.critical(f"Unhandled exception retrieving all prices for user {current_user.uid}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")


