# src/features/chat/domain/value_objects.py # Or enums.py / separate files

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass

from typing import Optional




# --- Value Objects ---

@dataclass(frozen=True) # Immutable
class ParticipantInfo:
    """Information about the external participant in the conversation."""
    sender_id: str # ID on the external platform
    sender_number: Optional[str] = None
    sender_nickname: Optional[str] = None

    def __post_init__(self):
        if not self.sender_id:
            raise ValueError("Participant sender_id cannot be empty.")

# Optional: If message content becomes complex
# @dataclass(frozen=True)
# class MessageContent:
#     text: str
#     # potentially other fields like attachments, media_type etc.

# Optional: If token tracking becomes complex
# @dataclass
# class TokenUsage:
#     user_tokens: int = 0
#     ai_tokens: int = 0

