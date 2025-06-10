# src/features/identity/application/commands/auth/change_email/change_email_command.py
from dataclasses import dataclass
from uuid import UUID

from src.core.base.command import BaseCommand


@dataclass
class RequestChangeEmailCommand(BaseCommand):
    """Command to request email change"""
    user_uid: UUID
    new_email: str