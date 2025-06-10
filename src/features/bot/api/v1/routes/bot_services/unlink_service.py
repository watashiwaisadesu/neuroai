# src/features/bot/api/routes/unlink_service_router.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from uuid import UUID

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status

from src.core.mediator.mediator import Mediator
from src.features.bot.api.v1.dtos.bot_service_management_dto import UnlinkServiceResponseDTO
from src.features.bot.application.commands.bot_services.unlink_service.unlink_service_command import \
    UnlinkServiceCommand
from src.features.identity.dependencies import get_current_user, get_role_checker


unlink_service_router = APIRouter()

@unlink_service_router.delete(
    "/{uid}/services/{service}",
    response_model=UnlinkServiceResponseDTO,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_role_checker(["user", "admin"]))],
    summary="Unlink a Service from a Bot",
)
@inject
async def unlink_service_from_bot(
    uid: UUID,  # bot UID
    service: UUID,
    current_user=Depends(get_current_user),
    mediator: Mediator = Depends(Provide["mediator"]),
):
    command = UnlinkServiceCommand(
        current_user_uid=current_user.uid,
        bot_uid=uid,
        service_uid=service
    )
    return await mediator.execute(command)
