# src/features/announcements/api/dtos/announcement_dtos.py
from enum import Enum

from pydantic import BaseModel, Field

from src.features.announcement.domain.entities.announcement_entity import AnnouncementType



class CreateAnnouncementRequestDTO(BaseModel):
    """
    Request DTO for creating a new announcement.
    """
    title: str = Field(..., description="The main title or headline of the announcement.")
    version: str = Field(..., description="A version identifier for the announcement (e.g., '1.2.0', 'Urgent Update').")
    text: str = Field(..., description="The full text content of the announcement.")
    type: AnnouncementType = Field(AnnouncementType.INFORMATION, description="The type of announcement (e.g., 'feature_release', 'maintenance', 'bug_fix', 'information', 'security_alert').")


