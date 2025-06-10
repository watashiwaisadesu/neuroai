# src/features/bot/domain/entities/bot_document_entity.py

import uuid
from typing import Optional, Any
from datetime import datetime

from src.core.models.base_entity import BaseEntity  # Adjust import path


class BotDocumentEntity(BaseEntity):
    """Represents a document associated with a Bot."""
    bot_uid: uuid.UUID
    filename: str
    content_type: Optional[str] = None
    # Option 1: Store file data directly (as in your example - not ideal for large files)
    file_data: Optional[bytes] = None  # For simplicity matching your example

    # Option 2: Store a reference (better for production)
    # storage_path: Optional[str] = None # e.g., "s3://bucket/bot_docs/bot_uid/filename"
    # file_size: Optional[int] = None

    def __init__(
            self,
            bot_uid: uuid.UUID,
            filename: str,
            uid: Optional[uuid.UUID] = None,
            created_at: Optional[datetime] = None,
            updated_at: Optional[datetime] = None,
            content_type: Optional[str] = None,
            file_data: Optional[bytes] = None,  # For Option 1
            # storage_path: Optional[str] = None, # For Option 2
            # file_size: Optional[int] = None,    # For Option 2
    ):
        super().__init__(uid=uid)
        if not bot_uid:
            raise ValueError("bot_uid cannot be empty for a document.")
        if not filename or not filename.strip():
            raise ValueError("Filename cannot be empty.")

        self.bot_uid = bot_uid
        self.filename = filename
        self.content_type = content_type
        self.file_data = file_data  # Option 1
        # self.storage_path = storage_path # Option 2
        # self.file_size = file_size       # Option 2

    # Add other domain methods if needed
