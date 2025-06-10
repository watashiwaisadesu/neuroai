# src/features/chat/api/dtos/process_incoming_message_dto.py (New file or add to existing chat DTOs)

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime

from src.features.conversation.domain.enums import ChatPlatform, MessageRole



# Response DTO (Optional - might just be success/failure or trigger other events)
class ProcessIncomingMessageResponseDTO(BaseModel):
    """Response after processing an incoming message."""
    conversation_uid: UUID
    user_message_uid: UUID
    ai_response_generated: bool = False
    ai_message_uid: Optional[UUID] = None
    # *** ADD THIS FIELD ***
    ai_response_content: Optional[str] = Field(None, description="The textual content of the AI's response, if generated.")
    message: str = "Message processed." # General status message

    model_config = { # Pydantic v2
        "json_schema_extra": {
            "example": {
                "conversation_uid": "71d10dcb-f5ae-45d7-8f13-bfdd12030035",
                "user_message_uid": "5009e4dd-c11b-4c1e-8b98-97467ac40da8",
                "ai_response_generated": True,
                "ai_message_uid": "08466b06-c2a5-4142-be11-6f9171865279",
                "ai_response_content": "This is the AI's answer.",
                "message": "Message processed successfully."
            }
        }
    }

