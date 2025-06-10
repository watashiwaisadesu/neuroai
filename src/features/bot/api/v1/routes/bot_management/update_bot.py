# src/features/bot/api/routes/update_bot_settings_router.py
from uuid import UUID

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status, HTTPException

from src.core.mediator.mediator import Mediator
from src.features.bot.api.v1.dtos.get_user_bots_dto import BotResponseDTO
from src.features.bot.api.v1.dtos.update_bot_dto import UpdateBotRequestDTO
from src.features.bot.application.commands.bot_management.update_bot.update_bot_command import UpdateBotCommand
from src.features.bot.exceptions.bot_exceptions import BotNotFoundError, BotAccessDeniedError, \
    InvalidBotAISettingsError, InvalidBotQuotaError, InvalidBotDetailsError
from src.features.identity.dependencies import get_role_checker, get_current_user
from src.features.identity.domain.entities.user_entity import UserEntity

update_bot_router = APIRouter()


@update_bot_router.patch(
    "/{uid}",
    response_model=BotResponseDTO,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_role_checker(["user", "admin"]))]
)
@inject
async def update_bot(
        uid: UUID,
        dto: UpdateBotRequestDTO,
        current_user: UserEntity = Depends(get_current_user),
        mediator: Mediator = Depends(Provide["mediator"]),
):
    """Update bot settings."""
    try:
        command = UpdateBotCommand(
            bot_uid=uid,
            user_uid=current_user.uid,
            update_data=dto
        )

        return await mediator.execute(command)

    except BotNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BotAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except (InvalidBotAISettingsError, InvalidBotQuotaError, InvalidBotDetailsError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update bot")