# src/features/integrations/telegram/api/routes/telegram_auth_routes.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends  # Import Body

from src.core.mediator.mediator import Mediator
from src.features.identity.dependencies import get_current_user
from src.features.identity.domain.entities.user_entity import UserEntity
from src.features.integrations.messengers.telegram.api.v1.dtos.telegram_auth_dtos import (
    TelegramVerificationCodeRequestDTO, )
from src.features.integrations.messengers.telegram.application.commands.submit_telegram_code.submit_telegram_code_command import \
    SubmitTelegramCodeCommand

submit_code_router = APIRouter()




@submit_code_router.post("/bots/{uid}/submit-code")
@inject
async def submit_telegram_login_code(
    uid: UUID,
    data: TelegramVerificationCodeRequestDTO,
    current_user: UserEntity = Depends(get_current_user),
    mediator: Mediator = Depends(Provide["mediator"]),
):
    command = SubmitTelegramCodeCommand(
        phone_number=data.phone_number,
        code=data.code,
        target_bot_uid=uid,
        current_user=current_user,
    )
    return await mediator.execute(command)
