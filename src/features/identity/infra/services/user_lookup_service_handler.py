# src/features/identity/infra/services/user_lookup_service_impl.py
from typing import Optional, List
from uuid import UUID

from src.features.bot.application.services.user_lookup_service import UserLookupService, UserInfo
from src.features.identity.domain.repositories.user_unit_of_work import UserUnitOfWork


class UserLookupServiceHandler(UserLookupService):
    def __init__(self, uow: UserUnitOfWork):
        self._user_unit_of_work = uow

    async def get_user_by_uid(self, uid: str) -> Optional[UserInfo]:
        async with self._user_unit_of_work:
            user = await self._user_unit_of_work.user_repository.find_by_uid(UUID(uid))
        if not user:
            return None

        return UserInfo(
            uid=str(user.uid),
            email=user.email,
            avatar_file_url=user.avatar_file_url,
            is_verified=user.is_verified,
        )

    async def get_users_by_uids(self, uids: List[str]) -> List[UserInfo]:
        uuid_list = [UUID(uid) for uid in uids]
        async with self._user_unit_of_work:
            users = await self._user_unit_of_work.user_repository.find_by_uids(uuid_list)

        return [
            UserInfo(
                uid=str(user.uid),
                email=user.email,
                avatar_file_url=user.avatar_file_url,
                is_verified=user.is_verified
            )
            for user in users
        ]

    async def find_user_by_email(self, email: str) -> Optional[UserInfo]:
        async with self._user_unit_of_work:
            user = await self._user_unit_of_work.user_repository.find_by_email(email)
        if not user:
            return None

        return UserInfo(
            uid=str(user.uid),
            email=user.email,
            avatar_file_url=user.avatar_file_url,
            is_verified=user.is_verified,
        )