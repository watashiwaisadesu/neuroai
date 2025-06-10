from typing import Optional

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status, Query

from src.core.mediator.mediator import Mediator
from src.di_container import ApplicationContainer
from src.features.conversation.api.v1.dtos.get_all_conversations_dto import GetConversationsResponseDTO
from src.features.conversation.application.queries.get_all_conversations.get_all_conversations_query import \
    GetAllConversationsQuery
from src.features.identity.dependencies import get_role_checker, get_current_user

get_all_conversations_router = APIRouter()

@get_all_conversations_router.get(
    "/",
    response_model=GetConversationsResponseDTO,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_role_checker(["user", "admin"]))],
    summary="Get All Accessible Conversations",
    description="Retrieves a list of conversations associated with bots the user can access, optionally filtered by platform."
)
@inject
async def get_all_conversations(
    user=Depends(get_current_user),
    platform: Optional[str] = Query(
        None, description="Filter conversations by platform (e.g., 'playground', 'telegram')."
    ),
    mediator: Mediator = Depends(Provide[ApplicationContainer.mediator])
):
    query = GetAllConversationsQuery(
        user=user.uid,
        platform_filter=platform
    )
    return await mediator.query(query)
