# src/features/bot/api/routes/bot_management/get_last_active_bots.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status, HTTPException

from src.core.mediator.mediator import Mediator
from src.features.bot.api.v1.dtos.get_user_bots_dto import GetLastActiveBotsResponse
from src.features.bot.application.queries.bot_management.get_last_active_bots.get_last_active_bots_query import \
    GetLastActiveBotsQuery
from src.features.identity.dependencies import get_current_user, get_role_checker
from src.features.identity.domain.entities.user_entity import UserEntity



last_active_bots_router = APIRouter()


@last_active_bots_router.get(
    "/last-active",
    response_model=GetLastActiveBotsResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_role_checker(["user", "admin"]))],
    summary="Get Last 5 Active Bots",
    description="Retrieves the 5 most recently updated bots accessible to the current user."
)
@inject
async def get_last_active_bots(
        current_user: UserEntity = Depends(get_current_user),
        mediator: Mediator = Depends(Provide["mediator"]),
):
    """
    API endpoint to fetch the last 5 active bots accessible by the user.
    """
    logger.info(f"Request received to get last active bots for user {current_user.uid}")

    try:
        query = GetLastActiveBotsQuery(
            user_uid=current_user.uid
        )
        response: GetLastActiveBotsResponse = await mediator.query(query)
        return response

    except Exception as e:
        logger.error(f"Failed to get last active bots: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve last active bots"
        )