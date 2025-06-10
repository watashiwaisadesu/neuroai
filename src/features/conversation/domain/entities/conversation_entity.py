# src/features/chat/domain/entities/conversation_entity.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
import uuid
from typing import List, Optional
from datetime import datetime

from src.core.models.base_entity import BaseEntity
from src.features.conversation.domain.enums import ChatPlatform
from src.features.conversation.domain.value_objects.participant_info import ParticipantInfo

from src.features.conversation.domain.entities.message_entity import MessageEntity



class ConversationEntity(BaseEntity):
    """
    Aggregate Root for a Conversation.
    Manages the conversation state and its messages.
    """
    # --- Identifiers ---
    # conversation_id: str # Using the external ID? Or internal UUID? Let's use internal UUID like other entities.
    owner_uid: uuid.UUID # Link to PlatformUserEntity UID
    bot_uid: uuid.UUID # Link to BotEntity UID

    # --- Core Attributes ---
    platform: ChatPlatform
    participant: ParticipantInfo # VO for external user info
    bot_name: Optional[str] = None # Copied at creation? Or looked up?
    crm_catalog_id: Optional[int] = None

    # --- Contained Entities ---
    # Use private attribute and provide controlled access methods
    _messages: List[MessageEntity]

    # --- Constructor ---
    def __init__(
        self,
        owner_uid: uuid.UUID,
        bot_uid: uuid.UUID,
        platform: ChatPlatform,
        participant: ParticipantInfo,
        uid: Optional[uuid.UUID] = None, # For BaseEntity
        created_at: Optional[datetime] = None, # For BaseEntity
        updated_at: Optional[datetime] = None, # For BaseEntity
        bot_name: Optional[str] = None,
        crm_catalog_id: Optional[int] = None,
        initial_messages: Optional[List[MessageEntity]] = None
    ):
        super().__init__(uid=uid)

        if not owner_uid: raise ValueError("owner_uid cannot be empty.")
        if not bot_uid: raise ValueError("bot_uid cannot be empty.")
        if not platform: raise ValueError("platform cannot be empty.")
        if not participant: raise ValueError("participant info cannot be empty.")

        self.owner_uid = owner_uid
        self.bot_uid = bot_uid
        self.platform = platform
        self.participant = participant
        self.bot_name = bot_name
        self.crm_catalog_id = crm_catalog_id
        self._messages = sorted(initial_messages or [], key=lambda m: m.timestamp) # Keep sorted
        logger.debug(f"ConversationEntity initialized (UID: {self.uid}) with {len(self._messages)} initial messages.")

    # --- Properties / Accessors ---
    @property
    def messages(self) -> List[MessageEntity]:
        """Provides read-only access to the sorted list of messages."""
        # Return a copy to prevent external modification
        return list(self._messages)

    # --- Methods (Behavior) ---
    def add_message(self, message: MessageEntity):
        """Adds a message to the conversation, maintaining order."""
        if not isinstance(message, MessageEntity):
            raise TypeError("Can only add MessageEntity objects.")

        # Prevent adding duplicate message IDs if necessary (check existing UIDs)
        if any(m.uid == message.uid for m in self._messages):
             logger.warning(f"Attempted to add duplicate message UID {message.uid} to conversation {self.uid}")
             return # Or raise error

        logger.debug(f"Adding message (UID: {message.uid}, Role: {message.role}) to conversation {self.uid}")
        self._messages.append(message)
        # Re-sort after adding, although append should maintain if timestamps are sequential
        self._messages.sort(key=lambda m: m.timestamp)
        self.update_timestamp() # Update conversation timestamp

    def get_last_message(self) -> Optional[MessageEntity]:
        """Returns the most recent message, if any."""
        return self._messages[-1] if self._messages else None

    def update_crm_id(self, crm_id: Optional[int]):
        """Updates the associated CRM ID."""
        if self.crm_catalog_id != crm_id:
             self.crm_catalog_id = crm_id
             self.update_timestamp()