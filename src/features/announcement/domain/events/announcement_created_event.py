# src/features/announcements/domain/events/announcement_events.py

import uuid
from dataclasses import dataclass

from src.core.mediator.event import BaseEvent  # Adjust path if needed


@dataclass(frozen=True)
class AnnouncementCreatedEvent(BaseEvent):
    """
    Domain event fired when a new announcement is created.
    """
    uid: uuid.UUID
    title: str
    version: str
    text: str
    type: str