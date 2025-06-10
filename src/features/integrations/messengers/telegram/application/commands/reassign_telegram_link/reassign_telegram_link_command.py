from uuid import UUID
from dataclasses import dataclass
from src.core.mediator.command import BaseCommand
from src.features.identity.domain.entities.user_entity import UserEntity # Adjust path as needed

@dataclass
class ReassignTelegramLinkCommand(BaseCommand):
    link_uid: str # The UID of the TelegramAccountLinkEntity to reassign
    new_bot_uid: UUID
    current_user: UserEntity # For authorization checks