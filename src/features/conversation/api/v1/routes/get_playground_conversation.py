# Ensure BotEntity is imported for type hinting in accessible_bots
# from src.features.identity.domain.entities.user_entity import UserEntity # If current_user needed directly

from uuid import UUID

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status, Path

from src.core.mediator.mediator import Mediator
from src.features.conversation.api.v1.dtos.get_single_conversation_dto import GetConversationResponseDTO
from src.features.conversation.application.queries.get_playground_conversation.get_playground_conversation_query import \
    GetPlaygroundConversationQuery
# Ensure BotEntity is imported for type hinting in accessible_bots
from src.features.identity.dependencies import get_role_checker, get_current_user  # Your existing dependency
from src.features.identity.domain.entities.user_entity import UserEntity

# from src.features.identity.domain.entities.user_entity import UserEntity # If current_user needed directly

get_playground_conversation_router = APIRouter()

@get_playground_conversation_router.get(
    "/playground/{bot_uid}", # Original path
    response_model=GetConversationResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get Single Playground Bot Conversation",
    description="Returns the single playground conversation for the specified bot_uid, if accessible.",
    dependencies=[
        Depends(get_role_checker(["user", "admin"])),
        # `accessible_bots` dependency will also implicitly handle some auth
    ]
)
@inject
async def get_single_playground_bot_conversation_route(
    bot_uid: UUID = Path(..., description="The UID of the Bot for its playground conversation."),
    current_user: UserEntity = Depends(get_current_user),
    mediator: Mediator = Depends(Provide["mediator"]),
):
    """
    API endpoint to retrieve the single playground conversation associated with a bot.
    """
    query = GetPlaygroundConversationQuery(
        bot_uid=bot_uid,
        user_uid=current_user.uid
    )
    return await mediator.query(query)