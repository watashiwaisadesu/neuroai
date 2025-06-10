# src/features/auth/domain/services/role_checker.py

from typing import List, Any

from src.features.identity.domain.entities.user_entity import UserEntity
from src.features.identity.exceptions.auth_exceptions import (
    AccountNotVerifiedError, InsufficientPermissionError
)


class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: UserEntity) -> Any:
        if not current_user.is_account_verified():
            raise AccountNotVerifiedError()
        if current_user.get_role() in self.allowed_roles:
            return True
        raise InsufficientPermissionError()
