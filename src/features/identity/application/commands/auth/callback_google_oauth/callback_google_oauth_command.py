# src/features/identity/application/commands/auth/callback_google_oauth/callback_google_oauth_command.py
from dataclasses import dataclass

from src.core.base.command import BaseCommand


@dataclass
class CallbackGoogleOauthCommand(BaseCommand):
    """Command to handle Google OAuth callback"""
    code: str