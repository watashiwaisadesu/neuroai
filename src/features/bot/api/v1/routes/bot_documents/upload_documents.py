from fastapi import APIRouter, Depends, UploadFile, File, status, HTTPException
from typing import List
from uuid import UUID
from dependency_injector.wiring import inject, Provide

from src.features.bot.api.v1.dtos.upload_documents_dto import UploadBotDocumentsResponseDTO
from src.features.bot.application.commands.bot_documents.upload_documents.upload_documents_command import UploadBotDocumentsCommand
from src.features.identity.dependencies import get_current_user
from src.features.identity.domain.entities.user_entity import UserEntity
from src.core.mediator.mediator import Mediator
from src.di_container import ApplicationContainer

upload_documents_router = APIRouter()


@upload_documents_router.post(
    "/{uid}/documents",
    response_model=UploadBotDocumentsResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Documents for a Bot"
)
@inject
async def upload_documents_for_bot(
    uid: UUID,
    files: List[UploadFile] = File(...),
    current_user: UserEntity = Depends(get_current_user),
    mediator: Mediator = Depends(Provide[ApplicationContainer.mediator]),
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    command = UploadBotDocumentsCommand(
        current_user_uid=current_user.uid,
        bot_uid=uid,
        files=files
    )
    return await mediator.execute(command)