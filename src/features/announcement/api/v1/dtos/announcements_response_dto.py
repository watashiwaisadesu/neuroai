# src/features/announcements/api/dtos/announcement_dtos.py

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

# Ensure this import path is correct for your AnnouncementEntity
from src.features.announcement.domain.entities.announcement_entity import AnnouncementEntity, AnnouncementType

class AnnouncementDTO(BaseModel):
    """
    Response DTO for an Announcement, representing its current state.
    """
    uid: uuid.UUID = Field(..., description="Unique identifier of the announcement.")
    title: str = Field(..., description="The main title or headline of the announcement.")
    version: str = Field(..., description="A version identifier for the announcement.")
    text: str = Field(..., description="The full text content of the announcement.")
    type: str = Field(..., description="The type of announcement. ")
    created_at: datetime = Field(..., description="Timestamp when the announcement record was created.")
    updated_at: datetime = Field(..., description="Timestamp when the announcement record was last updated.")

    class Config:
        from_attributes = True # Allows Pydantic to map fields directly from ORM/Entity instances

    @staticmethod
    def from_entity(entity: AnnouncementEntity) -> "AnnouncementDTO":
        """
        Converts an AnnouncementEntity domain entity into an AnnouncementResponseDTO.
        """
        return AnnouncementDTO(
            uid=entity.uid,
            title=entity.title,
            version=entity.version,
            text=entity.text,
            type=entity.type,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

class AnnouncementResponseDTO(BaseModel):
    message: str
    announcement: Optional[AnnouncementDTO] = None

class GetAnnouncementsResponseDTO(BaseModel):
    message: str
    announcements: Optional[List[AnnouncementDTO]] = None