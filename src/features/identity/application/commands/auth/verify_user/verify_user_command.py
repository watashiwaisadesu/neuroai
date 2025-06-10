# src/features/identity/application/commands/auth/verify_user/verify_user_command.py
from dataclasses import dataclass

from src.core.base.command import BaseCommand


@dataclass
class VerifyUserCommand(BaseCommand):
    token: str
