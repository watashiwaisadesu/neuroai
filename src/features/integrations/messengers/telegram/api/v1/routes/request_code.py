# src/features/integrations/telegram/api/routes/telegram_auth_routes.py

from uuid import UUID
from fastapi import APIRouter, Depends, status, Body, Path
from dependency_injector.wiring import inject, Provide

from src.core.mediator.mediator import Mediator
from src.features.identity.dependencies import get_current_user
from src.features.identity.domain.entities.user_entity import UserEntity
from src.features.integrations.messengers.telegram.api.v1.dtos.telegram_auth_dtos import (
    TelegramPhoneNumberRequestDTO,
    RequestTelegramCodeResponseDTO,
)

from src.features.integrations.messengers.telegram.application.commands.request_telegram_code.request_telegram_code_command import \
    RequestTelegramCodeCommand

request_code_router = APIRouter()

@request_code_router.post(
    "/bots/{uid}/request-code",
    response_model=RequestTelegramCodeResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Request Telegram Login Code",
    description="Initiates the Telegram login process by sending a code to the provided phone number."
)
@inject
async def request_telegram_login_code_route(
    uid: UUID = Path(...),
    data: TelegramPhoneNumberRequestDTO = Body(...),
    current_user: UserEntity = Depends(get_current_user),
    mediator: Mediator = Depends(Provide["mediator"]),
):
    command = RequestTelegramCodeCommand(
        bot_uid=uid,
        phone_number=str(data.phone_number),
        current_user=current_user,
    )
    return await mediator.execute(command)
