# 1. Command (src/features/bot/application/commands/bot_management/create_bot/create_bot_command.py)
from dataclasses import dataclass
from src.core.base.command import BaseCommand


@dataclass
class CreateBotCommand(BaseCommand):
    user_uid: str  # Creator's UID
    bot_type: str  # Type of bot to create