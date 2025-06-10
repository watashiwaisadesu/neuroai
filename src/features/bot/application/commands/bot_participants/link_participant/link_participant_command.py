# src/features/bot/application/commands/bot_participants/link_participant/link_participant_command.py
from dataclasses import dataclass
from uuid import UUID

from src.core.mediator.command import BaseCommand


@dataclass
class LinkBotParticipantCommand(BaseCommand):
    bot_uid: UUID
    user_uid: UUID  # User performing the action
    participant_email: str  # Email of user to add
    participant_role: str  # Role to assign