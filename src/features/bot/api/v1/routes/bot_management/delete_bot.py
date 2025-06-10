# src/features/bot/api/routes/delete_bot_router.py
from uuid import UUID

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status, HTTPException

from src.core.mediator.mediator import Mediator
from src.features.bot.api.v1.dtos.delete_bot_dto import DeleteBotResponseDTO
from src.features.bot.application.commands.bot_management.delete_bot.delete_bot_command import DeleteBotCommand
from src.features.bot.exceptions.bot_exceptions import BotNotFoundError, BotAccessDeniedError
from src.features.identity.dependencies import get_current_user, get_role_checker
from src.features.identity.domain.entities.user_entity import UserEntity

delete_bot_router = APIRouter()


@delete_bot_router.delete(
    "/{uid}",
    response_model=DeleteBotResponseDTO,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_role_checker(["user", "admin"]))]  # Basic role check
)
@inject
async def delete_bot(
        uid: UUID,
        current_user: UserEntity = Depends(get_current_user),
        mediator: Mediator = Depends(Provide["mediator"]),
):
    """Delete a bot by its UID."""
    try:
        command = DeleteBotCommand(
            bot_uid=uid,
            user_uid=current_user.uid
        )

        return await mediator.execute(command)

    except BotNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BotAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete bot")