# src/features/support/api/dtos/support_request_dtos.py

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict

from src.features.support.domain.entities.support_entity import SupportEntity
from src.features.support.domain.value_objects.support_enums import (
    SupportStatus, SupportPriority, SupportCategory
)


# Pydantic V2 config for enums if needed
class PydanticConfig:
    arbitrary_types_allowed = True # For Enums if not using __get_pydantic_core_schema__

# DTO for incoming request to create a support request
class CreateSupportRequestDTO(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True) # Apply for Pydantic V2 if enums are directly used

    email: Optional[EmailStr] = Field(None, description="Email of the user submitting the request. Defaults to current user's email if not provided.")
    subject: Optional[str] = Field(None, max_length=255, description="Brief subject line for the support request.")
    message: str = Field(..., description="The detailed message or description of the support issue.")
    category: Optional[SupportCategory] = Field(None, description="The category of the support request.")
    # Note: Images are handled separately via UploadFile in the endpoint,
    # and their URLs will be passed to the command/entity.


# DTO for representing a support request in responses
class SupportDTO(BaseModel):
    uid: uuid.UUID = Field(..., description="Unique identifier of the support request.")
    user_uid: uuid.UUID = Field(..., description="Unique identifier of the user who submitted the request.")
    email: EmailStr = Field(..., description="Email address associated with the request.")
    subject: Optional[str] = Field(None, description="Brief subject line for the support request.")
    message: str = Field(..., description="The detailed message of the support issue.")
    attachments: List[str] = Field(default_factory=list, description="List of URLs to attached files (e.g., images).")
    status: SupportStatus = Field(..., description="Current status of the support request.")
    priority: SupportPriority = Field(..., description="Priority level of the support request.")
    category: Optional[SupportCategory] = Field(None, description="Category of the support request.")
    created_at: datetime = Field(..., description="Timestamp when the support request was created.")
    updated_at: datetime = Field(..., description="Timestamp when the support request was last updated.")

    class Config:
        from_attributes = True # Enable Pydantic to map fields from ORM/Entity
        use_enum_values = True # Serialize enums to their string values

    @staticmethod
    def from_entity(entity: SupportEntity) -> "SupportDTO":
        """
        Converts a SupportRequestEntity domain entity into a SupportRequestDTO.
        """
        return SupportDTO(
            uid=entity.uid,
            user_uid=entity.user_uid,
            email=entity.email,
            subject=entity.subject,
            message=entity.message,
            attachments=entity.attachments,
            status=entity.status, # Pydantic will handle enum to string conversion with use_enum_values=True
            priority=entity.priority,
            category=entity.category,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


# General response DTO for operations that return a single support request
class SupportResponseDTO(BaseModel):
    message: str
    request: Optional[SupportDTO] = None

class SupportInitiatedResponseDTO(BaseModel):
    message: str = "Support request submission initiated successfully."
    request_id: uuid.UUID = Field(..., description="A unique ID to track the submission process.")
    status: str = "processing"

# Response DTO for listing multiple support requests
class ListSupportsResponseDTO(BaseModel):
    message: str
    requests: List[SupportDTO] = Field(default_factory=list)

