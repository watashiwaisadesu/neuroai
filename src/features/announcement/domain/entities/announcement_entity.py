from dataclasses import dataclass
from enum import Enum

from src.core.models.base_entity import BaseEntity


# Enums for announcement properties
class AnnouncementType(str, Enum):
    FEATURE_RELEASE = "feature_release"
    MAINTENANCE = "maintenance"
    BUG_FIX = "bug_fix"
    INFORMATION = "information"
    SECURITY_ALERT = "security_alert"


@dataclass
class AnnouncementEntity(BaseEntity):
    """
    Represents a system-wide announcement or news update.
    """
    title: str
    version: str
    text: str
    type: AnnouncementType = AnnouncementType.INFORMATION

    def __post_init__(self):
        super().__post_init__()  # Call post_init of BaseEntity if it has one
        if not self.title: raise ValueError("Announcement title cannot be empty.")
        if not self.version: raise ValueError("Announcement version cannot be empty.")
        if not self.text: raise ValueError("Announcement text cannot be empty.")

        if isinstance(self.type, str):
            try:
                self.type = AnnouncementType(self.type)
            except ValueError:
                raise ValueError(f"Invalid announcement type string: {self.type}")

        if self.type not in AnnouncementType:  # <--- Simplified check for Enum
            raise ValueError(f"Invalid announcement type: {self.type}")

    def update_content(self, new_title: str, new_version: str, new_text: str, new_type: AnnouncementType): # <--- Change new_type hint
        """Updates the content of the announcement."""
        if not new_title: raise ValueError("New title cannot be empty.")
        if not new_version: raise ValueError("New version cannot be empty.")
        if not new_text: raise ValueError("New text cannot be empty.")

        # Ensure new_type is coerced to AnnouncementType if it's a string
        if isinstance(new_type, str):
            try:
                new_type = AnnouncementType(new_type)
            except ValueError:
                raise ValueError(f"Invalid new announcement type string: {new_type}")

        if new_type not in AnnouncementType: # <--- Simplified check for Enum
            raise ValueError(f"Invalid announcement type: {new_type}")

        self.title = new_title
        self.version = new_version
        self.text = new_text
        self.type = new_type
        self.update_timestamp()