from dataclasses import dataclass
from uuid import UUID

from src.core.base.event import BaseEvent


@dataclass(frozen=True)
class UserRegisteredEvent(BaseEvent):
    user_uid: UUID
    email: str