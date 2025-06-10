from dataclasses import dataclass
from typing import List
from uuid import UUID

from src.core.base.command import BaseCommand

@dataclass
class DeleteBotDocumentsCommand(BaseCommand):
    current_user_uid: UUID
    bot_uid: UUID
    document_uids_to_delete: List[UUID]