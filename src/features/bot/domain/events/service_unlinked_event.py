# src/features/bot/domain/events/service_unlinked_event.py
from dataclasses import dataclass
from uuid import UUID
from src.core.base.event import BaseEvent

@dataclass(frozen=True)
class ServiceUnlinkedEvent(BaseEvent):
    service_uid: UUID
    platform: str
    linked_account_uid: UUID | None
