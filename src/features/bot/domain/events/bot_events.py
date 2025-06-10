# 3. Domain Events (src/features/bot/domain/events/bot_events.py)
from dataclasses import dataclass, field
from datetime import datetime
from src.core.base.event import BaseEvent


@dataclass(frozen=True)
class BotCreatedEvent(BaseEvent):
    """Event published when a new bot is created"""
    bot_uid: str
    owner_uid: str
    bot_type: str
    status: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class BotOwnerAssignedEvent(BaseEvent):
    """Event published when a user is assigned as bot owner"""
    bot_uid: str
    user_uid: str
    role: str
    assigned_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class BotExpirySetEvent(BaseEvent):
    """Event published to set bot expiry in cache"""
    bot_uid: str
    expiry_seconds: int
    set_at: datetime = field(default_factory=datetime.utcnow)