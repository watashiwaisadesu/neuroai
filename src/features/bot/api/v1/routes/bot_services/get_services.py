# src/features/bot/api/routes/get_services_route.py

from uuid import UUID

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status

from src.core.mediator.mediator import Mediator
from src.features.bot.api.v1.dtos.bot_service_management_dto import GetServicesResponseDTO
from src.features.bot.application.queries.bot_services.get_services.get_services_query import GetServicesQuery
from src.features.identity.dependencies import get_current_user, get_role_checker

get_services_router = APIRouter()


@get_services_router.get(
    "/{uid}/services",
    response_model=GetServicesResponseDTO,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_role_checker(["user", "admin"]))],
    summary="List Services Linked to a Bot"
)
@inject
async def list_linked_services(
    uid: UUID,
    current_user=Depends(get_current_user),
    mediator: Mediator = Depends(Provide["mediator"]),
):
    query = GetServicesQuery(bot_uid=uid, user_uid=current_user.uid)
    return await mediator.query(query)
