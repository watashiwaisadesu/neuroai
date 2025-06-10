from dataclasses import dataclass
from dataclasses import dataclass
from typing import Dict, Any

from src.core.base.command import BaseCommand


@dataclass
class RefreshTokenUserCommand(BaseCommand):
    """Command to refresh access token using refresh token"""
    token_data: Dict[str, Any]

