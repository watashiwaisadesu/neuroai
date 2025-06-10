from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Optional
# ... other DTO imports ...




class BotDocumentResponseItemDTO(BaseModel):
    """Represents a document linked to a bot."""
    document_uid: UUID = Field(..., description="UID of the document record.")
    # bot_uid: UUID # Usually not needed in the item if part of a bot's document list
    filename: str = Field(..., description="Original filename of the document.")
    content_type: Optional[str] = Field(None, description="MIME type of the document.")
    # created_at: datetime # Optional: if you want to show when it was uploaded

    model_config = { # Pydantic v2
        "json_schema_extra": {
            "example": {
                "document_uid": "doc_123e4567-e89b-12d3-a456-426614174000",
                "filename": "instructions.pdf",
                "content_type": "application/pdf"
            }
        }
    }