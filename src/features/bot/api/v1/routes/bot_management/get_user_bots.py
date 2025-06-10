# 4. Router (src/features/bot/api/routes/bot_management/get_user_bots.py)

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status

from src.core.mediator.mediator import Mediator
from src.features.bot.api.v1.dtos.get_user_bots_dto import GetUserBotsResponse
from src.features.bot.application.queries.bot_management.get_user_bots.get_user_bots_query import GetUserBotsQuery
from src.features.identity.dependencies import get_current_user, get_role_checker

get_user_bots_router = APIRouter()


@get_user_bots_router.get(
    "/",
    response_model=GetUserBotsResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_role_checker(["user", "admin"]))],
    responses={
        200: {
            "description": "List of user's bots retrieved successfully",
            "model": GetUserBotsResponse
        }
    }
)
@inject
async def get_user_bots(
    current_user=Depends(get_current_user),
    mediator: Mediator = Depends(Provide["mediator"]),
):
    """Get all bots accessible to the current user"""
    query = GetUserBotsQuery(user_uid=current_user.uid)
    return await mediator.query(query)