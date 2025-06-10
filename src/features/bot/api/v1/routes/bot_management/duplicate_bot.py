# src/features/bot/api/routes/duplicate_bot_router.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from uuid import UUID

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status, HTTPException

from src.core.mediator.mediator import Mediator
from src.features.bot.api.v1.dtos.get_user_bots_dto import BotResponseDTO
from src.features.bot.application.commands.bot_management.duplicate_bot.duplicate_bot_command import DuplicateBotCommand
from src.features.bot.exceptions.bot_exceptions import BotNotFoundError, BotAccessDeniedError
from src.features.identity.dependencies import get_current_user, get_role_checker
from src.features.identity.domain.entities.user_entity import UserEntity


duplicate_bot_router = APIRouter()


@duplicate_bot_router.post(
    "/{uid}/duplicate",
    response_model=BotResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_role_checker(["user", "admin"]))],
    summary="Duplicate a bot by UID",
    description="""Duplicates the specified bot if the current user has access.
    The duplicate will belong to the current user and start in 'draft' status.
    Returns the newly created Bot info."""
)
@inject
async def duplicate_bot(
        uid: UUID,
        current_user: UserEntity = Depends(get_current_user),
        mediator: Mediator = Depends(Provide["mediator"]),
):
    """Duplicate a bot."""
    logger.info(f"User {current_user.uid} requesting duplication of bot {uid}")

    try:
        command = DuplicateBotCommand(
            bot_uid=uid,
            user_uid=str(current_user.uid)
        )

        return await mediator.execute(command)

    except BotNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BotAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to duplicate bot: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to duplicate bot")