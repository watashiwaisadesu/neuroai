# src/features/identity/application/commands/auth/verify_email/verify_email_command.py
from dataclasses import dataclass

from src.core.base.command import BaseCommand


@dataclass
class VerifyEmailCommand(BaseCommand):
    """Command to verify email change"""
    token: str