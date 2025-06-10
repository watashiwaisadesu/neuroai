# src/features/support/domain/entities/support_attachment_entity.py

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Type, TypeVar

from src.core.models.base_entity import BaseEntity # Assuming your BaseEntity

T_Attachment = TypeVar('T_Attachment', bound='SupportAttachmentEntity')

@dataclass
class SupportAttachmentEntity(BaseEntity):
    """
    Represents an individual attachment for a support request in the domain model.
    """
    support_uid: uuid.UUID # Foreign key to the parent SupportRequestEntity
    file_url: str
    file_name: Optional[str] = None
    content_type: Optional[str] = None
    size_bytes: Optional[int] = None

    def __post_init__(self):
        super().__post_init__()
        if not self.support_uid:
            raise ValueError("Support request UID cannot be empty for an attachment.")
        if not self.file_url:
            raise ValueError("File URL cannot be empty for an attachment.")
        # Add more validation here if needed, e.g., for valid URL format

    @classmethod
    def create(
        cls: Type[T_Attachment],
        support_uid: uuid.UUID,
        file_url: str,
        file_name: Optional[str] = None,
        file_size: Optional[int] = None,
        content_type: Optional[str] = None,
        size_bytes: Optional[int] = None,
    ) -> T_Attachment:
        """
        Factory method to create a new SupportAttachmentEntity instance.
        """
        if not isinstance(support_uid, uuid.UUID):
            raise TypeError("support_request_uid must be a UUID.")
        if not file_url:
            raise ValueError("File URL must be provided.")

        instance = cls(
            support_uid=support_uid,
            file_url=file_url,
            file_name=file_name,
            content_type=content_type,
            size_bytes=size_bytes,
            # uid, created_at, updated_at will be handled by BaseEntity's __post_init__ or defaults
        )
        return instance

