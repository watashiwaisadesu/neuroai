# src/features/bot/application/commands/bot_participants/unlink_participant/unlink_participant_command.py
from dataclasses import dataclass
from uuid import UUID

from src.core.mediator.command import BaseCommand


@dataclass
class UnlinkBotParticipantCommand(BaseCommand):
    bot_uid: UUID
    current_user_uid: UUID  # User performing the action
    participant_user_uid: UUID  # User to remove