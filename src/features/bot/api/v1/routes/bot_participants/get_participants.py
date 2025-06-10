from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from uuid import UUID

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status, HTTPException

from src.core.mediator.mediator import Mediator
from src.features.bot.api.v1.dtos.get_participants_dto import GetParticipantsDTO
# The GetBotParticipantsInputDTO might not be needed if query takes primitive types directly
# from src.features.bot.api.dtos.get_participants_dto import GetBotParticipantsInputDTO
from src.features.bot.application.queries.bot_participants.get_participants.get_bot_participants_query import \
    GetBotParticipantsQuery
from src.features.bot.exceptions.bot_exceptions import BotNotFoundError, BotAccessDeniedError
from src.features.identity.dependencies import get_current_user, get_role_checker  # , get_role_checker # if needed
from src.features.identity.domain.entities.user_entity import UserEntity



# If you have a router specifically for participant operations under a bot
# e.g., /bots/{uid}/participants, this can be part of that.
# Otherwise, adjust the prefix as needed.
get_participants_router = APIRouter(
    # prefix="/bots", # Example if this router is mounted at /bots
    tags=["Bot Participants"]
)


@get_participants_router.get(
    "/{bot_uid}/participants",  # Consistent with link_participant route structure
    response_model=GetParticipantsDTO,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_role_checker(["user", "admin"]))],
    summary="Get Participants for a Bot",
    description="Retrieves a list of users participating in the specified bot, including their role, email, and avatar. Requires the current user to have appropriate access to the bot."
)
@inject
async def get_bot_participants(
        bot_uid: UUID,
        current_user: UserEntity = Depends(get_current_user),
        mediator: Mediator = Depends(Provide["mediator"]),
):
    """
    API endpoint to fetch participants for a specific bot using the mediator pattern.
    """
    logger.info(f"User {current_user.uid} requesting to list participants for bot '{bot_uid}'")

    try:
        query = GetBotParticipantsQuery(
            bot_uid=bot_uid,
            current_user_uid=current_user.uid # Pass current user's UID for access checks in handler
        )

        # Execute the query via the mediator
        participant_list = await mediator.query(query)
        return participant_list

    except BotNotFoundError as e:
        logger.warning(f"Get participants failed for bot {bot_uid}: Bot not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BotAccessDeniedError as e:
        logger.warning(f"Get participants failed for bot {bot_uid}: Access denied for user {current_user.uid}.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    # Add other specific exception handling as needed
    except Exception as e:
        logger.error(f"Failed to get participants for bot {bot_uid}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve participants")

