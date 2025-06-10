from dataclasses import dataclass
from uuid import UUID
from typing import List
from fastapi import UploadFile


@dataclass
class UploadBotDocumentsCommand:
    current_user_uid: UUID
    bot_uid: UUID
    files: List[UploadFile]
