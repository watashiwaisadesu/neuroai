# src/features/identity/domain/events/email_change_events.py
from dataclasses import dataclass
from uuid import UUID

from src.core.base.event import BaseEvent


@dataclass(frozen=True)
class EmailChangeRequestedEvent(BaseEvent):
    """Event fired when user requests email change"""
    user_uid: UUID
    new_email: str
    confirmation_token: str