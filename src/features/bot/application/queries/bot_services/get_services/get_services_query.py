from dataclasses import dataclass
from uuid import UUID

from src.core.base.query import BaseQuery


@dataclass
class GetServicesQuery(BaseQuery):
    user_uid: UUID
    bot_uid: UUID