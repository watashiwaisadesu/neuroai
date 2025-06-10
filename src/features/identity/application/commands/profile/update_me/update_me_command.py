# 1. Command (src/features/identity/application/commands/profile/update_me/update_me_command.py)
from dataclasses import dataclass
from typing import Dict, Any, Optional
from src.core.base.command import BaseCommand


@dataclass
class UpdateMeCommand(BaseCommand):
    user_uid: str  # Current user's UID
    update_data: Dict[str, Any]  # Fields to update

    def __post_init__(self):
        # Validate that update_data is not empty
        if not self.update_data:
            raise ValueError("Update data cannot be empty")