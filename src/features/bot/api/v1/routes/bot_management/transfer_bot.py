# src/features/bot/api/routes/bot_management/transfer_bot.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from uuid import UUID

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status, HTTPException

from src.core.mediator.mediator import Mediator
from src.features.bot.api.v1.dtos.get_user_bots_dto import BotResponseDTO
from src.features.bot.api.v1.dtos.transfer_bot_dto import TransferBotRequestDTO
from src.features.bot.application.commands.bot_management.transfer_bot.transfer_bot_command import TransferBotCommand
from src.features.bot.exceptions.bot_exceptions import (
    BotNotFoundError,
    BotAccessDeniedError,
    CannotTransferToSelfError,
    NewOwnerNotFoundError
)
from src.features.identity.dependencies import get_current_user, get_role_checker
from src.features.identity.domain.entities.user_entity import UserEntity



transfer_bot_router = APIRouter()


@transfer_bot_router.post(
    "/{uid}/transfer",
    response_model=BotResponseDTO,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_role_checker(["user", "admin"]))],
    summary="Transfer Bot Ownership",
    description="Transfers ownership of the specified bot to another user (identified by email). Requires the current user to be an owner or admin of the bot."
)
@inject
async def transfer_bot_ownership(
        uid: UUID,
        transfer_data: TransferBotRequestDTO,
        current_user: UserEntity = Depends(get_current_user),
        mediator: Mediator = Depends(Provide["mediator"]),
):
    """Transfer ownership of a bot."""
    logger.info(
        f"User {current_user.uid} requesting to transfer bot '{uid}' to email '{transfer_data.new_owner_email}'.")

    try:
        command = TransferBotCommand(
            bot_uid=uid,
            user_uid=str(current_user.uid),
            new_owner_email=transfer_data.new_owner_email
        )

        return await mediator.execute(command)

    except BotNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BotAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except NewOwnerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CannotTransferToSelfError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to transfer bot: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to transfer bot ownership")
