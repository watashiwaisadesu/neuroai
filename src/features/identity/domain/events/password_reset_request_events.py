from dataclasses import dataclass

from src.core.base.event import BaseEvent


@dataclass(frozen=True)
class PasswordResetRequestedEvent(BaseEvent):
    """Event fired when user requests password reset"""
    email: str
    reset_token: str