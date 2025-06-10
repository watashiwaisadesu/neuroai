# src/features/identity/application/queries/get_user_avatar_query.py
from dataclasses import dataclass
from uuid import UUID

from src.core.base.query import BaseQuery
from src.features.identity.api.v1.dtos.profile.get_me_dto import UserResponseDTO # Assuming UserResponseDTO is where MinimalUserDTO is


@dataclass(frozen=True)
class GetMeAvatarQuery(BaseQuery): # The expected return type is a string (URL)
    """
    Query to retrieve the avatar URL for a specific user.
    """
    user_uid: UUID