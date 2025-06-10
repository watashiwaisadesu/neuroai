from dataclasses import dataclass
from uuid import UUID

from src.core.mediator.query import BaseQuery  # Assuming your BaseQuery


@dataclass(frozen=True)
class GetPlatformPricesQuery(BaseQuery):
    """Query to retrieve all platform prices."""
    user_uid: UUID # Context for security/auditing
