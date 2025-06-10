# src/features/announcements/application/commands/create_announcement/create_announcement_command.py

from dataclasses import dataclass

from src.core.mediator.command import BaseCommand
from src.features.announcement.domain.entities.announcement_entity import AnnouncementType

@dataclass
class CreateAnnouncementCommand(BaseCommand):
    """
    Command to create a new announcement.
    """
    title: str
    version: str
    text: str
    type: AnnouncementType