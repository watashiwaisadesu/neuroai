# src/features/identity/domain/events/oauth_events.py
from dataclasses import dataclass
from uuid import UUID

from src.core.base.event import BaseEvent


@dataclass(frozen=True)
class OAuthUserRegisteredEvent(BaseEvent):
    """Event fired when a new user is created via OAuth"""
    user_uid: UUID
    email: str
    provider: str  # 'google', 'facebook', etc.
    user_type: str


@dataclass(frozen=True)
class OAuthLoginSuccessfulEvent(BaseEvent):
    """Event fired when OAuth login is successful"""
    user_uid: UUID
    email: str
    provider: str
    is_new_user: bool