# src/features/bot/application/commands/bot_management/delete_bot/delete_bot_command.py
from dataclasses import dataclass
from uuid import UUID

from src.core.base.command import BaseCommand


@dataclass
class DeleteBotCommand(BaseCommand):
    bot_uid: UUID
    user_uid: UUID