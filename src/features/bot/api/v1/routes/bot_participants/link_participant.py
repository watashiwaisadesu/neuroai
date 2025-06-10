# src/features/bot/api/routes/bot_participants/link_participant.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from uuid import UUID

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status, HTTPException

from src.core.mediator.mediator import Mediator
from src.features.bot.api.v1.dtos.link_participant_dto import LinkBotParticipantRequestDTO, LinkBotParticipantResponseDTO
from src.features.bot.application.commands.bot_participants.link_participant.link_participant_command import \
    LinkBotParticipantCommand
from src.features.bot.exceptions.bot_exceptions import (
    BotNotFoundError,
    BotAccessDeniedError,
    ParticipantAlreadyExistsError,
    CannotAddOwnerAsParticipantError
)
from src.features.identity.dependencies import get_current_user, get_role_checker
from src.features.identity.domain.entities.user_entity import UserEntity
from src.features.identity.exceptions.user_exceptions import UserNotFoundError



link_participant_router = APIRouter()


@link_participant_router.post(
    "/{uid}/participants",
    response_model=LinkBotParticipantResponseDTO,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_role_checker(["user", "admin"]))],
    summary="Add a User as a Participant to a Bot",
    description="Adds a user (identified by email) as a participant to the specified bot with a given role. Requires the current user to be an owner or admin of the bot."
)
@inject
async def link_bot_participant(
        uid: UUID,
        participant_data: LinkBotParticipantRequestDTO,
        current_user: UserEntity = Depends(get_current_user),
        mediator: Mediator = Depends(Provide["mediator"]),
):
    """Add a participant to a bot."""
    logger.info(f"User {current_user.uid} requesting to add participant '{participant_data.email}' to bot '{uid}'")

    try:
        command = LinkBotParticipantCommand(
            bot_uid=uid,
            user_uid=current_user.uid,
            participant_email=participant_data.email,
            participant_role=participant_data.role
        )

        return await mediator.execute(command)

    except BotNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BotAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ParticipantAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except CannotAddOwnerAsParticipantError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        # Domain validation errors (e.g., invalid role)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to add participant: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add participant")

