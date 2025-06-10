# src/features/integrations/telegram/application/services/telethon_client_service.py (New file)

from abc import ABC, abstractmethod
from typing import Optional, Callable, Any, Dict, Awaitable # Import Awaitable
from uuid import UUID

from src.features.integrations.messengers.telegram.application.services.telegram_event_handler_service import \
    TelegramEventHandlerService


class TelethonClientService(ABC):
    """
    Abstracts interactions with the Telethon library for managing
    Telegram client sessions and operations.
    """

    @abstractmethod
    async def request_login_code(
        self,
        phone_number: str,
        # api_id: int, # These will come from settings within the implementation
        # api_hash: str
    ) -> Dict[str, Any]:
        """
        Requests a login code from Telegram for the given phone number.
        Returns a dictionary containing 'phone_code_hash' and a 'temporary_session_string'.
        """
        raise NotImplementedError

    @abstractmethod
    async def submit_login_code(
        self,
        phone_number: str,
        code: str,
        phone_code_hash: str,
        temporary_session_string: str, # The session used to request the code
        # api_id: int,
        # api_hash: str
    ) -> Dict[str, Any]:
        """
        Submits the login code to Telegram to finalize authentication.
        Returns a dictionary containing 'final_session_string', 'telegram_user_id', 'username'.
        """
        raise NotImplementedError


    @abstractmethod
    async def start_message_listener(
        self,
        service_uid: UUID,
        session_string: str,
        bot_uid: UUID, # Our internal bot UID for context
        event_handler_service: TelegramEventHandlerService
    ) -> Any: # Returns a representation of the running client/task for management
        """
        Connects using the session string, starts listening for incoming messages,
        and dispatches them to the event_handler_service.
        Manages the client.run_until_disconnected() loop.
        """
        raise NotImplementedError

    @abstractmethod
    async def stop_message_listener(self,service_uid: UUID) -> None:
        """Stops an active message listener and disconnects the client."""
        raise NotImplementedError

    @abstractmethod
    async def get_me(self, session_string: str) -> Optional[Dict[str, Any]]:
        """
        Gets details of the currently logged-in Telegram user for a given session.
        Returns dict with 'id', 'username', 'phone', etc. or None.
        """
        raise NotImplementedError

    @abstractmethod
    async def is_user_authorized(self, session_string: str) -> bool:
        """Checks if the client for the given session is authorized."""
        raise NotImplementedError


