# src/features/support/infra/persistence/models/support_request_orm.py

import uuid
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Make sure you import the enum values or define them directly here if needed
# For mapped_column, it's often cleaner to store the enum value as a string.
from src.features.support.domain.value_objects.support_enums import (
    SupportStatus, SupportPriority
)
from src.infra.persistence.models.sqlalchemy_base import SQLAlchemyBase
if TYPE_CHECKING:
    from src.features.support.infra.persistence.models.support_attachment_orm import SupportAttachmentORM


class SupportORM(SQLAlchemyBase):
    """
    SQLAlchemy ORM model for the SupportRequestEntity.
    Maps the SupportRequestEntity to the 'support_requests' table in the database.
    """
    __tablename__ = "support_items"

    user_uid: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    subject: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # New field
    attachments: Mapped[List["SupportAttachmentORM"]] = relationship(
        "SupportAttachmentORM",
        backref="support_request",  # Allows access from attachment back to request: attachment.support_request
        cascade="all, delete-orphan",  # Important: When a request is deleted, its attachments are deleted.
        # When an attachment is removed from the list, it's deleted from DB.
        lazy="joined"  # Eagerly load attachments when loading a SupportRequestORM
    )

    # Store enum values as strings in the database
    status: Mapped[str] = mapped_column(String, nullable=False, default=SupportStatus.OPEN.value)
    priority: Mapped[str] = mapped_column(String, nullable=False, default=SupportPriority.MEDIUM.value)
    category: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Stores enum value as string


    def __repr__(self):
        return (
            f"<SupportRequestORM(uid={self.uid}, user_uid={self.user_uid}, "
            f"status='{self.status}', priority='{self.priority}')>"
        )