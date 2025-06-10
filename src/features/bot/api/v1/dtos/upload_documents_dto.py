# src/features/bot/api/dtos/bot_document_dto.py (New file)

from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Optional
from fastapi import UploadFile  # For type hinting in InputDTO

# Import entities for internal DTO
from src.features.bot.domain.entities.bot_entity import BotEntity


class UploadedDocumentInfoDTO(BaseModel):
    """Information about a single successfully uploaded document."""
    document_uid: UUID
    filename: str


class UploadBotDocumentsResponseDTO(BaseModel):
    """Response after attempting to upload documents."""
    message: str
    documents: List[UploadedDocumentInfoDTO] = Field(default_factory=list)


# Internal Input DTO for the Use Case/Command
class UploadBotDocumentsInputDTO(BaseModel):
    """Internal DTO carrying necessary data for the upload documents use case."""
    target_bot_entity: BotEntity
    files: List[UploadFile]  # List of files from FastAPI

    class Config:
        arbitrary_types_allowed = True
