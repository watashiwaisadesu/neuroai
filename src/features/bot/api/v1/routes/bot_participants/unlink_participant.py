# src/features/bot/api/routes/bot_participants/unlink_participant.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from uuid import UUID

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status, HTTPException, Path

from src.core.mediator.mediator import Mediator
from src.features.bot.api.v1.dtos.remove_bot_participant_dto import UnlinkBotParticipantResponseDTO
from src.features.bot.application.commands.bot_participants.unlink_participant.unlink_participant_command import \
    UnlinkBotParticipantCommand
from src.features.bot.exceptions.bot_exceptions import (
    BotNotFoundError,
    BotAccessDeniedError,
    ParticipantNotFoundError,
    CannotUnlinkOwnerError
)
from src.features.identity.dependencies import get_current_user, get_role_checker
from src.features.identity.domain.entities.user_entity import UserEntity



unlink_participant_router = APIRouter()


@unlink_participant_router.delete(
    "/{uid}/participants/{user_uid}",
    response_model=UnlinkBotParticipantResponseDTO,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_role_checker(["user", "admin"]))],
    summary="Remove a Participant from a Bot",
    description="Removes a specified user from the participant list of a bot. Requires the current user to be an owner or admin of the bot. Cannot remove the bot owner."
)
@inject
async def delete_bot_participant(
        uid: UUID = Path(..., title="Bot UID", description="The UID of the bot."),
        user_uid: UUID = Path(..., title="User UID", description="The UID of the participant user to remove."),
        current_user: UserEntity = Depends(get_current_user),
        mediator: Mediator = Depends(Provide["mediator"]),
):
    """Remove a participant from a bot."""
    logger.info(f"User {current_user.uid} requesting to remove participant '{user_uid}' from bot '{uid}'")

    try:
        command = UnlinkBotParticipantCommand(
            bot_uid=uid,
            current_user_uid=current_user.uid,
            participant_user_uid=user_uid
        )

        return await mediator.execute(command)

    except BotNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BotAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ParticipantNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CannotUnlinkOwnerError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to remove participant: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to remove participant")

