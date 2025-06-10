#src/features/identity/application/queries/profile/get_me/get_me_query
from dataclasses import dataclass
from src.core.base.query import BaseQuery


@dataclass(frozen=True)
class GetMeQuery(BaseQuery):
    user_uid: str  # Just pass the user ID, not the entire entity