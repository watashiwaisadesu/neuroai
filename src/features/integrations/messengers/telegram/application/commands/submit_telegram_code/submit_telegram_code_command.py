# src/features/integrations/messengers/telegram/application/commands/submit_telegram_code/submit_telegram_code_command.py

from dataclasses import dataclass
from uuid import UUID

from src.core.mediator.command import BaseCommand
from src.features.identity.domain.entities.user_entity import UserEntity


@dataclass
class SubmitTelegramCodeCommand(BaseCommand):
    target_bot_uid: UUID
    current_user: UserEntity
    phone_number: str
    code: str
