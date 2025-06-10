# src/features/bot/application/commands/bot_management/duplicate_bot/duplicate_bot_command.py
from dataclasses import dataclass
from uuid import UUID

from src.core.mediator.command import BaseCommand


@dataclass
class DuplicateBotCommand(BaseCommand):
    bot_uid: UUID
    user_uid: UUID