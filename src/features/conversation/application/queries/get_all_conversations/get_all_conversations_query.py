from dataclasses import dataclass
from uuid import UUID

from src.core.base.query import BaseQuery


@dataclass
class GetAllConversationsQuery(BaseQuery):
    user: UUID
    platform_filter: str | None
