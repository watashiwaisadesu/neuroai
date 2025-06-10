# 1. Command (src/features/identity/application/commands/profile/update_avatar/update_avatar_command.py)
from dataclasses import dataclass
from fastapi import UploadFile
from src.core.base.command import BaseCommand


@dataclass
class UpdateAvatarCommand(BaseCommand):
    user_uid: str
    avatar_file_data: bytes
    filename: str
    content_type: str

