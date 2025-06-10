
# src/features/support/api/dtos/support_dtos.py (or a new file like get_support_requests_dto.py)

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from src.features.support.domain.value_objects.support_enums import SupportCategory # Assuming this enum exists
from src.features.support.domain.value_objects.support_enums import SupportStatus # Assuming this enum exists, e.g., PENDING, RESOLVED

@dataclass(frozen=True)
class SupportDTO:
    """
    DTO for representing a support request in query responses.
    """
    uid: UUID
    user_uid: UUID
    email: str
    subject: Optional[str]
    message: str
    category: Optional[SupportCategory]
    status: SupportStatus # E.g., PENDING, RESOLVED, IN_PROGRESS
    created_at: datetime
    updated_at: datetime
    attachment_urls: List[str]