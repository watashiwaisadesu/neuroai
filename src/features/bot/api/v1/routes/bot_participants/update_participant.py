from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from uuid import UUID

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status, HTTPException, Path

from src.core.mediator.mediator import Mediator
from src.features.bot.api.v1.dtos.update_participant_dto import (
    UpdateBotParticipantRoleRequestDTO,
    UpdateBotParticipantRoleResponseDTO
)
from src.features.bot.application.commands.bot_participants.update_participant.update_participant_command import \
    UpdateBotParticipantRoleCommand
from src.features.bot.exceptions.bot_exceptions import (
    BotNotFoundError,
    BotAccessDeniedError,
    ParticipantNotFoundError,
    CannotUpdateOwnerRoleError
)
from src.features.identity.dependencies import get_current_user, get_role_checker
from src.features.identity.domain.entities.user_entity import UserEntity



update_participant_router = APIRouter()


@update_participant_router.patch(
    "/{uid}/participants/{user_uid}",
    response_model=UpdateBotParticipantRoleResponseDTO,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_role_checker(["user", "admin"]))],
    summary="Update a Participant's Role in a Bot",
    description="Updates the role for a specified user within a bot. Requires the current user to be an owner or admin of the bot. Cannot change the owner's role."
)
@inject
async def update_bot_participant_role(
        role_update_data: UpdateBotParticipantRoleRequestDTO,
        uid: UUID = Path(..., title="Bot UID", description="The UID of the bot."),
        user_uid: UUID = Path(..., title="Participant User UID",
                              description="The UID of the participant user whose role to update."),
        current_user: UserEntity = Depends(get_current_user),
        mediator: Mediator = Depends(Provide["mediator"]),
):
    """Update a participant's role in a bot."""
    logger.info(
        f"User {current_user.uid} requesting to update role for participant '{user_uid}' in bot '{uid}' to '{role_update_data.role.value}'")

    try:
        command = UpdateBotParticipantRoleCommand(
            bot_uid=uid,
            current_user_uid=str(current_user.uid),
            participant_user_uid=user_uid,
            new_role=role_update_data.role
        )

        return await mediator.execute(command)

    except BotNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BotAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ParticipantNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CannotUpdateOwnerRoleError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        # Domain validation errors (e.g., invalid role)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update participant role: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to update participant role")