from dataclasses import dataclass
from uuid import UUID

from src.core.base.query import BaseQuery


@dataclass(frozen=True)
class GetUserBotsQuery(BaseQuery):
    user_uid: UUID  # User requesting their bots