from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.core.base.command import BaseCommand
from src.features.conversation.domain.enums import ChatPlatform

@dataclass
class ProcessIncomingMessageCommand(BaseCommand):
    bot_uid: UUID
    platform: ChatPlatform
    sender_id: str
    content: str
    timestamp: datetime
    sender_number: str
    sender_nickname: str