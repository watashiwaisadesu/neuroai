# src/features/identity/domain/events/user_avatar_events.py

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from fastapi import UploadFile
from src.core.base.event import BaseEvent


@dataclass(frozen=True)
class UserAvatarUploadRequestedEvent(BaseEvent):
    """Domain event - user requested avatar upload"""
    request_id: str  # Unique ID to track this upload request
    user_uid: str
    email: str
    file_name: str
    avatar_file_data: bytes
    content_type: Optional[str] = None
    requested_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class UserAvatarUploadCompletedEvent(BaseEvent):
    """Infrastructure event - avatar was successfully uploaded to storage"""
    user_uid: str
    request_id: str
    file_url: str
    file_size: Optional[int] = None
    content_type: Optional[str] = None
    uploaded_at: datetime = field(default_factory=datetime.utcnow)


# @dataclass(frozen=True)
# class UserAvatarChangedEvent(BaseEvent):
#     """Domain event - user's avatar URL was changed in the system"""
#     user_uid: str
#     email: str
#     old_avatar_url: Optional[str]
#     new_avatar_url: str
#     changed_at: datetime = field(default_factory=datetime.utcnow)