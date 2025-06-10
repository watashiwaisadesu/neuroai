# src/features/integrations/telegram/domain/entities/telegram_account_link_entity.py

import uuid
from typing import Optional
from datetime import datetime, timezone

from src.core.models.base_entity import BaseEntity # Adjust import path

class TelegramAccountLinkEntity(BaseEntity):
    """
    Represents a link between an internal BotEntity and a specific Telegram user account session.
    """
    bot_uid: uuid.UUID # UID of the BotEntity this Telegram account is linked to
    platform_user_uid: uuid.UUID # UID of the PlatformUserEntity who owns the bot (for context/scoping)
    telegram_user_id: str # The unique user ID from Telegram (e.g., "123456789")
    phone_number: str # The phone number associated with this Telegram account
    username: Optional[str] = None # Optional: Telegram username
    session_string: Optional[str] = None # Telethon session string
    phone_code_hash: Optional[str] = None # Temporary, used during login
    is_active: bool = False # Is this link/listener currently active?
    last_connected_at: Optional[datetime] = None
    # Removed app_id as API credentials will come from config

    def __init__(
        self,
        bot_uid: uuid.UUID,
        platform_user_uid: uuid.UUID,
        phone_number: str,
        telegram_user_id: Optional[str] = None,
        uid: Optional[uuid.UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        username: Optional[str] = None,
        session_string: Optional[str] = None,
        phone_code_hash: Optional[str] = None,
        is_active: bool = False,
        last_connected_at: Optional[datetime] = None
    ):
        super().__init__(uid=uid)
        if not bot_uid: raise ValueError("bot_uid cannot be empty.")
        if not platform_user_uid: raise ValueError("platform_user_uid cannot be empty.")
        # telegram_user_id can be None initially if only phone is known
        if not phone_number: raise ValueError("phone_number cannot be empty.")

        self.bot_uid = bot_uid
        self.platform_user_uid = platform_user_uid
        self.telegram_user_id = telegram_user_id
        self.phone_number = phone_number
        self.username = username
        self.session_string = session_string
        self.phone_code_hash = phone_code_hash
        self.is_active = is_active
        self.last_connected_at = last_connected_at

    def activate_session(self, session_string: str, telegram_user_id: str, username: Optional[str]):
        """Activates the session after successful login."""
        self.session_string = session_string
        self.telegram_user_id = telegram_user_id
        self.username = username
        self.phone_code_hash = None # Clear after use
        self.is_active = True
        self.last_connected_at = datetime.now(timezone.utc)
        self.update_timestamp()

    def deactivate_session(self):
        """Deactivates the session, e.g., on logout or error."""
        # self.session_string = None # Optionally clear session string on deactivation
        self.is_active = False
        self.update_timestamp()

    def set_phone_code_hash(self, hash_val: str, temp_session_string: str):
        """Stores the phone_code_hash and temporary session during login."""
        self.phone_code_hash = hash_val
        self.session_string = temp_session_string # Store temp session for sign_in
        self.is_active = False # Not active until code is submitted
        self.update_timestamp()

