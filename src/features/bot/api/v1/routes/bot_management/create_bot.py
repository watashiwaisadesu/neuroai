# 5. Router (src/features/bot/api/routes/create_bot_router.py)
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status

from src.core.mediator.mediator import Mediator
from src.features.bot.api.v1.dtos.create_bot_dto import CreateBotRequestDTO, CreateBotResponseDTO
from src.features.bot.application.commands.bot_management.create_bot.create_bot_command import CreateBotCommand
from src.features.identity.dependencies import get_current_user, get_role_checker

create_bot_router = APIRouter()


@create_bot_router.post(
    "/",
    response_model=CreateBotResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_role_checker(["user", "admin"]))],
    responses={
        201: {
            "description": "Bot created successfully",
            "model": CreateBotResponseDTO
        }
    }
)
@inject
async def create_bot(
        body: CreateBotRequestDTO,
        current_user=Depends(get_current_user),
        mediator: Mediator = Depends(Provide["mediator"]),
):
    """Create a new bot"""
    command = CreateBotCommand(
        user_uid=str(current_user.uid),
        bot_type=body.bot_type
    )

    return await mediator.execute(command)