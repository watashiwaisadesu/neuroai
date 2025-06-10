from uuid import UUID

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status

from src.core.mediator.mediator import Mediator
from src.features.bot.api.v1.dtos.bot_service_management_dto import (
    LinkServiceRequestDTO,
    LinkServiceResponseDTO,
)
from src.features.bot.application.commands.bot_services.link_service.link_service_command import LinkServiceCommand
from src.features.identity.dependencies import get_current_user, get_role_checker

link_service_router = APIRouter()


@link_service_router.post(
    "/{uid}/services/",
    response_model=LinkServiceResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_role_checker(["user", "admin"]))],
    summary="Link a Service to a Bot",
)
@inject
async def link_service_to_bot(
    uid: UUID,  # Bot UID
    link_data: LinkServiceRequestDTO,
    current_user=Depends(get_current_user),
    mediator: Mediator = Depends(Provide["mediator"]),
):
    command = LinkServiceCommand(
        current_user_uid=current_user.uid,
        bot_uid=uid,
        request_data=link_data,
    )
    return await mediator.execute(command)