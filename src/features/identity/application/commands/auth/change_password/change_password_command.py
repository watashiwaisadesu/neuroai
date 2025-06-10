from dataclasses import dataclass

from src.core.base.command import BaseCommand
from src.features.identity.domain.entities.user_entity import UserEntity


@dataclass
class ChangePasswordCommand(BaseCommand):
    """Command to change user password"""
    current_password: str
    new_password: str
    confirm_new_password: str
    current_user: UserEntity