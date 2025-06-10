from enum import Enum

# --- Enums ---

class MessageRole(str, Enum):
    """Role of the sender of a message."""
    USER = "user"
    ASSISTANT = "assistant" # Your AI/Bot
    SYSTEM = "system" # System messages, instructions etc.

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

class ChatPlatform(str, Enum):
    """Supported chat platforms (Example)."""
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    INSTAGRAM = "instagram"
    PLAYGROUND = "playground" # From your previous example
    UNKNOWN = "unknown"
    # Add other platforms

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))
