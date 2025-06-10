# src/features/identity/application/commands/auth/reset_password_confirm/reset_password_confirm_command.py
from dataclasses import dataclass

from src.core.base.command import BaseCommand
from src.features.identity.api.v1.dtos.auth.reset_password_confirm_dto import VerifyResetPasswordRequestDTO


@dataclass
class VerifyPasswordCommand(BaseCommand):
    """Command to verify and confirm password reset"""
    token: str
    data: VerifyResetPasswordRequestDTO