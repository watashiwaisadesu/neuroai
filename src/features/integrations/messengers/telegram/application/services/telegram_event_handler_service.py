from abc import ABC, abstractmethod
from typing import Optional, Callable, Any, Dict, Awaitable # Import Awaitable
from uuid import UUID

# Interface for the service that processes raw Telethon events
class TelegramEventHandlerService(ABC):
    @abstractmethod
    async def handle_new_telethon_message(self, event: Any, telethon_client_instance: Any, associated_bot_uid: UUID, service_uid: UUID):
        """Processes a raw new message event from Telethon."""
        raise NotImplementedError