# src/features/integrations/messengers/telegram/application/commands/request_telegram_code/request_telegram_code_command.py
from dataclasses import dataclass
from uuid import UUID

from src.core.base.command import BaseCommand
from src.features.identity.domain.entities.user_entity import UserEntity


@dataclass
class RequestTelegramCodeCommand(BaseCommand):
    bot_uid: UUID
    phone_number: str
    current_user: UserEntity