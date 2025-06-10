# src/features/support/application/commands/create_support_request/create_support_request_command.py
from dataclasses import dataclass
from typing import List, Optional, Dict, Union  # Import Dict and Union for type hinting
from uuid import UUID

from pydantic import EmailStr

from src.core.mediator.command import BaseCommand
from src.features.support.domain.value_objects.support_enums import SupportCategory

AttachmentData = Dict[str, Union[bytes, str]]

@dataclass
class CreateSupportCommand(BaseCommand):
    """
    Command to create a new support request with pre-read attachment data.
    """
    user_uid: UUID
    email: EmailStr
    message: str
    subject: Optional[str] = None
    attachments: Optional[List[AttachmentData]] = None # Changed from List[UploadFile]
    category: Optional[SupportCategory] = None