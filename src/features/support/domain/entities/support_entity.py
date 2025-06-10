# src/features/support/domain/entities/support_request_entity.py

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, Type, TypeVar

from src.core.models.base_entity import BaseEntity # Assuming your BaseEntity
from src.features.support.domain.entities.support_attachment_entity import SupportAttachmentEntity
from src.features.support.domain.value_objects.support_enums import (
    SupportStatus, SupportPriority, SupportCategory
)

T = TypeVar('T', bound='SupportRequestEntity')

@dataclass
class SupportEntity(BaseEntity):
    """
    Represents a technical support request in the domain model.
    """
    user_uid: uuid.UUID
    email: str
    message: str
    subject: Optional[str] = None # A brief subject for the request
    attachments: List[SupportAttachmentEntity] = field(default_factory=list)
    status: SupportStatus = SupportStatus.OPEN
    priority: SupportPriority = SupportPriority.MEDIUM
    category: Optional[SupportCategory] = None # Optional category

    def __post_init__(self):
        super().__post_init__()
        if not self.message:
            raise ValueError("Support request message cannot be empty.")
        if not self.email:
            raise ValueError("Support request email cannot be empty.")
        if not self.user_uid:
            raise ValueError("User UID cannot be empty.")

        # Ensure enums are correctly typed if they were passed as strings
        if isinstance(self.status, str):
            self.status = SupportStatus(self.status)
        if isinstance(self.priority, str):
            self.priority = SupportPriority(self.priority)
        if isinstance(self.category, str) and self.category is not None:
            self.category = SupportCategory(self.category)

    @classmethod
    def create(
            cls: Type[T],
            uid: uuid.UUID,
            user_uid: uuid.UUID,
            email: str,
            message: str,
            subject: Optional[str] = None,
            attachments: Optional[List[SupportAttachmentEntity]] = None,
            status: SupportStatus = SupportStatus.OPEN,
            priority: SupportPriority = SupportPriority.MEDIUM,
            category: Optional[SupportCategory] = None,
    ) -> T:
        """
        Factory method to create a new SupportRequestEntity instance directly.
        Handles default values, initial validation, and timestamp generation.
        """
        # --- Pre-instantiation Validation ---
        if not isinstance(user_uid, uuid.UUID):
            raise TypeError("user_uid must be a UUID.")
        if not email or "@" not in email:  # Basic email validation
            raise ValueError("Invalid email address provided.")
        if not message:
            raise ValueError("Support request message cannot be empty.")

        # Handle default for mutable arguments (important for `attachments`)
        if attachments is None:
            attachments = []

        # --- Direct Instantiation ---
        # We call the class constructor directly with the validated and default arguments.
        # The __post_init__ will then run automatically after this.
        instance = cls(
            uid=uid,
            user_uid=user_uid,
            email=email,
            message=message,
            subject=subject,
            attachments=attachments,
            status=status,
            priority=priority,
            category=category,
            # IMPORTANT: If uid, created_at, updated_at are not handled by BaseEntity's
            # defaults/__post_init__, you would generate them here and pass them:
            # uid=uuid.uuid4(),
            # created_at=datetime.now(timezone.utc),
            # updated_at=datetime.now(timezone.utc),
        )
        return instance


    def update_status(self, new_status: SupportStatus):
        """Updates the status of the support request."""
        if not isinstance(new_status, SupportStatus):
            raise ValueError("New status must be a valid SupportRequestStatus enum member.")
        self.status = new_status
        self.update_timestamp()

    def update_priority(self, new_priority: SupportPriority):
        """Updates the priority of the support request."""
        if not isinstance(new_priority, SupportPriority):
            raise ValueError("New priority must be a valid SupportRequestPriority enum member.")
        self.priority = new_priority
        self.update_timestamp()


    def add_attachments(self, new_attachments: List[SupportAttachmentEntity]): # Changed parameter name and type
        """Adds new attachment entities to the support item."""
        self.attachments.extend(new_attachments)
        self.update_timestamp()
