# src/features/support/infra/persistence/models/support_attachment_orm.py

import uuid
from typing import Optional

from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infra.persistence.models.sqlalchemy_base import SQLAlchemyBase

class SupportAttachmentORM(SQLAlchemyBase):
    """
    SQLAlchemy ORM model for individual support request attachments.
    Maps to the 'support_attachments' table.
    """
    __tablename__ = "support_attachments"

    # Foreign key to link back to the SupportRequestORM
    # This column explicitly stores the UUID of the associated support request.
    support_uid: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("support_items.uid"), # Link to the primary key of support_requests table
        nullable=False,
        index=True # Index this for efficient lookups from support requests
    )

    # The S3 URL where the file is stored
    file_url: Mapped[str] = mapped_column(String(2048), nullable=False) # URL can be long, so a larger string size

    # Optional metadata about the file (good practice for future flexibility)
    file_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    content_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    size_bytes: Mapped[Optional[int]] = mapped_column(nullable=True)


    def __repr__(self):
        return (
            f"<SupportAttachmentORM(uid={self.uid}, "
            f"support_request_uid={self.support_uid}, "
            f"file_url='{self.file_url[:50]}...')>" # Truncate for cleaner repr
        )

