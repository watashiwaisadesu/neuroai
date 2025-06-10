from dataclasses import dataclass
from typing import Dict, Any

from src.core.base.command import BaseCommand


@dataclass
class LogoutUserCommand(BaseCommand):
    """Command to logout a user by blocklisting their token"""
    token_data: Dict[str, Any]