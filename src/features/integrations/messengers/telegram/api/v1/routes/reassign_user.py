# src/features/integrations/messengers/telegram/api/routes/telegram_management.py (New File or existing one)
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status, HTTPException

from src.core.mediator.mediator import Mediator
from src.features.identity.dependencies import get_current_user
from src.features.identity.domain.entities.user_entity import UserEntity  # Assuming your user model
from src.features.integrations.messengers.telegram.api.v1.dtos.reassign_telegram_link_dto import \
    ReassignTelegramLinkRequestDTO, TelegramAccountLinkResponseDTO
from src.features.integrations.messengers.telegram.application.commands.reassign_telegram_link.reassign_telegram_link_command import \
    ReassignTelegramLinkCommand
from src.features.integrations.messengers.telegram.exceptions.telegram_exceptions import TelegramResourceNotFoundError, \
    TelegramAuthError


reassign_telegram_link_router = APIRouter()

@reassign_telegram_link_router.patch(
    "/accounts/{link_uid}/reassign",
    response_model=TelegramAccountLinkResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Reassigns a Telegram account link to a different bot.",
    description="Allows an existing Telegram account link to be moved from its current bot to a new bot. Requires admin/owner role for the target bot.",
)
@inject
async def reassign_telegram_account_link(
    link_uid: str,
    request: ReassignTelegramLinkRequestDTO,
    current_user: UserEntity = Depends(get_current_user),
    mediator: Mediator = Depends(Provide["mediator"]),
):
    """
    Handles the request to reassign a Telegram account link to a new bot.
    """
    try:
        command = ReassignTelegramLinkCommand(
            link_uid=link_uid,
            new_bot_uid=request.new_bot_uid,
            current_user=current_user,
        )
        response = await mediator.execute(command)
        return response
    except TelegramResourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except TelegramAuthError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message) # Or 401 Unauthorized
    except Exception as e:
        logger.exception("Failed to reassign Telegram account link.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to reassign Telegram account link.")