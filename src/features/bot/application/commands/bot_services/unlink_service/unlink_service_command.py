from dataclasses import dataclass
from uuid import UUID
from src.core.base.command import BaseCommand

@dataclass
class UnlinkServiceCommand(BaseCommand):
    current_user_uid: UUID
    bot_uid: UUID
    service_uid: UUID