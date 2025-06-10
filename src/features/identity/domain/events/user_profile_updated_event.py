# 3. Event (src/features/identity/domain/events/user_events.py)
from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime

from src.core.base.event import BaseEvent


@dataclass(frozen=True)
class UserProfileUpdatedEvent(BaseEvent):
    user_uid: str
    email: str
    updated_fields: List[str]
    old_values: Dict[str, Any]
    new_values: Dict[str, Any]
    updated_at: datetime = field(default_factory=datetime.utcnow)