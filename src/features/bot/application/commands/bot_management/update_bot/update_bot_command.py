# src/features/bot/application/commands/bot_management/update_bot/update_bot_command.py
from dataclasses import dataclass
from uuid import UUID

from src.core.mediator.command import BaseCommand
from src.features.bot.api.v1.dtos.update_bot_dto import UpdateBotRequestDTO


@dataclass
class UpdateBotCommand(BaseCommand):
    bot_uid: UUID
    user_uid: UUID
    update_data: UpdateBotRequestDTO