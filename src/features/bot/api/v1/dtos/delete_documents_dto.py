# src/features/bot/api/dtos/bot_document_dto.py (Add to this existing file)

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Optional
from fastapi import UploadFile

# Import entities for internal DTO
from src.features.bot.domain.entities.bot_entity import BotEntity



# --- Existing DTOs ---
# class UploadedDocumentInfoDTO(BaseModel): ...
# class UploadBotDocumentsResponseDTO(BaseModel): ...
# class UploadBotDocumentsInputDTO(BaseModel): ...

# --- NEW DTOs for Deleting Documents ---

class DeleteBotDocumentsRequestDTO(BaseModel):
    """Request body for deleting bot documents."""
    document_uids: List[UUID] = Field(..., description="A list of document UIDs to delete.", min_length=1)

class DeleteBotDocumentsResponseDTO(BaseModel):
    """Response after attempting to delete documents."""
    message: str
    deleted_document_uids: List[UUID] = Field(default_factory=list)
    not_found_document_uids: List[UUID] = Field(default_factory=list) # Optional: to report UIDs not found

    model_config = { # Pydantic v2
        "json_schema_extra": {
            "example": {
                "message": "2 document(s) deleted successfully. 1 document(s) not found.",
                "deleted_document_uids": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "123e4567-e89b-12d3-a456-426614174001"
                ],
                "not_found_document_uids": [
                    "00000000-0000-0000-0000-000000000000"
                ]
            }
        }
    }

# Internal Input DTO for the Use Case/Command
class DeleteBotDocumentsInputDTO(BaseModel):
    """Internal DTO carrying necessary data for the delete documents use case."""
    target_bot_entity: BotEntity
    document_uids_to_delete: List[UUID]

    class Config:
        arbitrary_types_allowed = True
