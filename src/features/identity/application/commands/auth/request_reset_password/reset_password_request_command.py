from dataclasses import dataclass

from src.core.base.command import BaseCommand


@dataclass
class RequestResetPasswordCommand(BaseCommand):
    """Command to request password reset"""
    email: str