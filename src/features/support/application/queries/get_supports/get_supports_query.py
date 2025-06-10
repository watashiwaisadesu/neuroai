# src/features/support/application/queries/get_support_requests/get_support_requests_query.py

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from src.core.mediator.query import BaseQuery  # Assuming BaseQuery is defined here
from src.features.support.domain.value_objects.support_enums import SupportCategory  # Assuming this enum exists


@dataclass(frozen=True)
class GetSupportsQuery(BaseQuery):
    """
    Query to retrieve a list of support requests for a given user,
    optionally filtered by category.
    """
    user_uid: UUID
    category: Optional[SupportCategory] = None
    # Add pagination/sorting parameters here if needed, e.g.:
    # skip: int = 0
    # limit: int = 100