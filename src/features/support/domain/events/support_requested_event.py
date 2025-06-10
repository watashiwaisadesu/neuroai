import uuid
from dataclasses import dataclass
from typing import List, Optional, Dict, Union # Import Dict and Union for type hinting

from src.core.mediator.event import BaseEvent # Assuming your BaseEvent
from src.features.support.domain.value_objects.support_enums import SupportCategory

# Define a type alias for clarity for each attachment
AttachmentData = Dict[str, Union[bytes, str]]

@dataclass(frozen=True)
class SupportRequestedEvent(BaseEvent):
    """
    Event raised when a user submits a new support request.
    This triggers the file upload process using pre-read byte data.
    """
    uid: uuid.UUID
    user_uid: uuid.UUID
    email: str
    subject: Optional[str]
    message: str
    category: Optional[SupportCategory] # Assuming SupportCategory is correctly imported
    attachments: List[AttachmentData] # Changed from List[UploadFile] to List[AttachmentData]