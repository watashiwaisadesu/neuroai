# src/features/bot/domain/entities/bot_participant_entity.py

import uuid
from typing import Optional
from datetime import datetime # Import if using timestamps from BaseEntity

# Assuming BaseEntity handles uid, created_at, updated_at
from src.core.models.base_entity import BaseEntity

class BotParticipantEntity(BaseEntity):
    """
    Represents a user participating in a bot, defining their role.
    This is likely an Entity within the Bot Aggregate, or its own Aggregate
    depending on complexity, but often managed via the Bot aggregate.
    """
    bot_uid: uuid.UUID
    user_uid: uuid.UUID
    role: str # e.g., "viewer", "editor", "admin"

    def __init__(
        self,
        bot_uid: uuid.UUID,
        user_uid: uuid.UUID,
        role: str,
        uid: Optional[uuid.UUID] = None, # For BaseEntity
        created_at: Optional[datetime] = None, # For BaseEntity
        updated_at: Optional[datetime] = None, # For BaseEntity
    ):
        super().__init__(uid=uid)

        if not bot_uid:
            raise ValueError("bot_uid cannot be empty.")
        if not user_uid:
            raise ValueError("user_uid cannot be empty.")
        if not role or not role.strip():
            raise ValueError("Participant role cannot be empty.")

        self.bot_uid = bot_uid
        self.user_uid = user_uid
        self.role = role

    def change_role(self, new_role: str):
        """Updates the participant's role."""
        if not new_role or not new_role.strip():
            raise ValueError("New role cannot be empty.")
        if self.role != new_role:
            self.role = new_role
            self.update_timestamp()

