from dataclasses import dataclass
from uuid import UUID

from src.core.mediator.query import BaseQuery


@dataclass
class GetLastActiveBotsQuery(BaseQuery):
    user_uid: UUID  # User requesting their last active bots