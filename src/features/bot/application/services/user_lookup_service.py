from abc import ABC, abstractmethod
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class UserInfo:
    """DTO for user information needed by Bot context"""
    uid: str
    email: str
    avatar_file_url: Optional[str]
    is_verified: bool

class UserLookupService(ABC):
    @abstractmethod
    async def get_user_by_uid(self, uid: str) -> Optional[UserInfo]:
        pass

    @abstractmethod
    async def get_users_by_uids(self, uids: List[str]) -> List[UserInfo]:
        pass

    @abstractmethod
    async def find_user_by_email(self, email: str) -> Optional[UserInfo]:
        pass