from dataclasses import dataclass
from uuid import UUID

from src.core.mediator.command import BaseCommand


@dataclass
class TransferBotCommand(BaseCommand):
    bot_uid: UUID
    user_uid: UUID
    new_owner_email: str