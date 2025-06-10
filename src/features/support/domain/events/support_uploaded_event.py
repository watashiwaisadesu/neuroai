import uuid
from dataclasses import dataclass
from typing import List, Optional, Dict, Union

from src.core.mediator.event import BaseEvent  # Assuming your BaseEvent
from src.features.support.domain.value_objects.support_enums import SupportCategory

UploadedAttachmentData = Dict[str, Union[str, int]] # url, filename, content_type, file_size

@dataclass(frozen=True, kw_only=True)
class SupportUploadedEvent(BaseEvent):
    """Event raised after support request attachments have been successfully uploaded."""
    uid: uuid.UUID
    user_uid: uuid.UUID
    email: str
    subject: Optional[str]
    message: str
    category: Optional[SupportCategory]
    attachments_data: List[UploadedAttachmentData]