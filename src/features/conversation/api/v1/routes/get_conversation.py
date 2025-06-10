# src/features/conversation/api/routes/get_single_bot_conversation_router.py

from fastapi import APIRouter, Depends, status, Path
from uuid import UUID

from src.core.mediator.mediator import Mediator
from src.di_container import ApplicationContainer
from src.features.conversation.application.queries.get_single_conversation.get_single_conversation_query import \
    GetSingleBotConversationQuery
from src.features.identity.domain.entities.user_entity import UserEntity
from src.features.identity.dependencies import get_current_user, get_role_checker

from src.features.conversation.api.v1.dtos.get_single_conversation_dto import GetConversationResponseDTO

from dependency_injector.wiring import inject, Provide

get_conversation_router = APIRouter()

@get_conversation_router.get(
    "/{uid}",
    response_model=GetConversationResponseDTO,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_role_checker(["user", "admin"]))],
    summary="Get Single Bot Conversation",
    description="Returns a single conversation by its ID, ensuring the user has access to the associated bot."
)
@inject
async def get_conversation(
    uid: UUID = Path(..., description="Conversation UID"),
    current_user: UserEntity = Depends(get_current_user),
    mediator: Mediator = Depends(Provide[ApplicationContainer.mediator]),
):
    query = GetSingleBotConversationQuery(
        conversation_uid=uid,
        user_uid=current_user.uid
    )
    return await mediator.query(query)
