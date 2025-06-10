
# src/features/chat/domain/entities/message_entity.py

import uuid
from typing import Optional
from datetime import datetime, timezone

# Import base entity, Enums, VOs
from src.core.models.base_entity import BaseEntity # Adjust import path
from src.features.conversation.domain.enums import MessageRole


class MessageEntity(BaseEntity):
    """
    Represents a single message within a Conversation aggregate.
    """
    # conversation_id: uuid.UUID # Link back to ConversationEntity UID
    role: MessageRole
    content: str # Or MessageContent VO
    timestamp: datetime
    # Optional: Track token usage per message
    tokens_user: Optional[int] = 0
    tokens_ai: Optional[int] = 0
    # Or use TokenUsage VO: token_usage: TokenUsage

    def __init__(
        self,
        role: MessageRole,
        content: str, # Or MessageContent
        timestamp: Optional[datetime] = None,
        uid: Optional[uuid.UUID] = None, # For BaseEntity
        created_at: Optional[datetime] = None, # For BaseEntity
        updated_at: Optional[datetime] = None, # For BaseEntity
        tokens_user: int = 0,
        tokens_ai: int = 0
        # token_usage: Optional[TokenUsage] = None # If using VO
    ):
        super().__init__(uid=uid)

        if not role: raise ValueError("Message role cannot be empty.")
        if content is None: raise ValueError("Message content cannot be None.") # Allow empty string?

        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now(timezone.utc) # Ensure timezone aware
        self.tokens_user = tokens_user
        self.tokens_ai = tokens_ai
        # self.token_usage = token_usage or TokenUsage() # If using VO

    # Add methods if needed (e.g., validation on content)