from dataclasses import dataclass
from uuid import UUID

from src.core.mediator.command import BaseCommand
from src.features.bot.domain.enums import BotParticipantRole


@dataclass
class UpdateBotParticipantRoleCommand(BaseCommand):
    bot_uid: UUID
    current_user_uid: UUID  # User performing the action
    participant_user_uid: UUID  # User whose role to update
    new_role: BotParticipantRole  # New role to assign