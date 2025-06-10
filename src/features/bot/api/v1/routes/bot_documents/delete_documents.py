from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException

from src.features.bot.api.v1.dtos.delete_documents_dto import (
    DeleteBotDocumentsRequestDTO, DeleteBotDocumentsResponseDTO
)
from src.features.bot.application.commands.bot_documents.delete_documents.delete_documents_command import DeleteBotDocumentsCommand
from src.features.identity.dependencies import get_current_user
from src.features.identity.domain.entities.user_entity import UserEntity
from dependency_injector.wiring import inject, Provide
from src.core.mediator.mediator import Mediator
from src.di_container import ApplicationContainer


delete_documents_router = APIRouter()


@delete_documents_router.delete(
    "/{uid}/documents",
    response_model=DeleteBotDocumentsResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Delete Specified Documents for a Bot",
    description="Deletes one or more documents associated with the bot based on their UIDs. Requires owner/admin/editor access."
)
@inject
async def delete_documents_for_bot(
    uid: UUID,
    delete_request: DeleteBotDocumentsRequestDTO,
    current_user: UserEntity = Depends(get_current_user),
    mediator: Mediator = Depends(Provide[ApplicationContainer.mediator]),
):
    if not delete_request.document_uids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No document_uids provided.")

    logger.info(f"Request to delete documents {delete_request.document_uids} for bot '{uid}' by user {current_user.uid}")

    # Pass user uid + bot uid + document uids in the input DTO (adapt this DTO if needed)
    command = DeleteBotDocumentsCommand(
        current_user_uid=current_user.uid,
        bot_uid=uid,
        document_uids_to_delete=delete_request.document_uids
    )
    return await mediator.execute(command)
