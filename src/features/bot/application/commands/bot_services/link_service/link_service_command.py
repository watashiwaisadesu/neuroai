# link_service_command.py
from dataclasses import dataclass
from uuid import UUID

from src.core.base.command import BaseCommand
from src.features.bot.api.v1.dtos.bot_service_management_dto import LinkServiceRequestDTO


@dataclass
class LinkServiceCommand(BaseCommand):
    current_user_uid: UUID
    bot_uid: UUID
    request_data: LinkServiceRequestDTO
