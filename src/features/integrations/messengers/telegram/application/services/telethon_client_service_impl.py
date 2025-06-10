# src/features/integrations/telegram/application/services/telethon_client_service_impl.py (New file)

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
import asyncio
from typing import Optional, Callable, Any, Dict, Awaitable
from uuid import UUID

from telethon import TelegramClient, events, errors as telethon_errors
from telethon.sessions import StringSession

from src.features.integrations.messengers.telegram.application.services.telegram_event_handler_service import \
    TelegramEventHandlerService
# Import interface and event handler service interface
from src.features.integrations.messengers.telegram.application.services.telethon_client_service import TelethonClientService

# Import settings for API credentials
from src.config import Settings
# Import custom exceptions
from src.features.integrations.messengers.telegram.exceptions.telegram_exceptions import (
    TelegramConnectionError,
    TelegramAuthError,
    TelegramRateLimitError,
    TelegramResourceNotFoundError,
    TelegramGenericError, TelegramAppCredentialsNotSetError
)



_active_listener_tasks: Dict[UUID, asyncio.Task] = {}  # Key: service_uid
_active_clients: Dict[UUID, TelegramClient] = {}      # Key: service_uid


class TelethonClientServiceImpl(TelethonClientService):
    """
    Implementation of ITelethonClientService using the Telethon library.
    Manages client connections, login, message sending, and listening.
    """
    _settings: Settings
    _api_id: int
    _api_hash: str

    def __init__(self, settings: Settings):
        self._settings = settings
        if not self._settings.TELEGRAM_API_ID or not self._settings.TELEGRAM_API_HASH:
            logger.error("Telegram API ID or API Hash is not configured in settings.")
            raise TelegramAppCredentialsNotSetError("Telegram API ID or API Hash is not configured.")
        try:
            self._api_id = int(self._settings.TELEGRAM_API_ID)  # Ensure it's an int
            self._api_hash = self._settings.TELEGRAM_API_HASH
        except ValueError:
            logger.error("TELEGRAM_API_ID in settings must be an integer.")
            raise TelegramAppCredentialsNotSetError("TELEGRAM_API_ID must be an integer.")
        logger.debug("TelethonClientServiceImpl initialized with API credentials from settings.")

    async def _create_client(self, session_string: Optional[str] = None) -> TelegramClient:
        """Helper to create and configure a Telethon client."""
        session = StringSession(session_string) if session_string else StringSession()
        client = TelegramClient(
            session,
            self._api_id,
            self._api_hash,
            # device_model="YourAppName", # Optional: Customize as needed
            # system_version="1.0.0",
            # app_version="1.0.0"
        )
        logger.debug(f"TelethonClient created (session provided: {bool(session_string)})")
        return client

    async def request_login_code(self, phone_number: str) -> Dict[str, Any]:
        logger.info(f"Requesting Telegram login code for phone: {phone_number}")
        client = await self._create_client()
        try:
            logger.debug(f"Connecting client for code request to {phone_number}...")
            await client.connect()
            if not client.is_connected():
                raise TelegramConnectionError("Failed to connect to Telegram for code request.")

            logger.debug(f"Sending code request to {phone_number}...")
            # The result of send_code_request is an object, not a coroutine
            result = await client.send_code_request(phone_number)
            temp_session_string = client.session.save()
            logger.info(f"Code sent to {phone_number}. Phone code hash obtained: {result.phone_code_hash}")
            return {
                "phone_code_hash": result.phone_code_hash,
                "temporary_session_string": temp_session_string  # This session is for THIS phone number's login process
            }
        except telethon_errors.FloodWaitError as e:
            logger.error(f"FloodWaitError for {phone_number}: {e.seconds}s", exc_info=True)
            raise TelegramRateLimitError(wait_seconds=e.seconds) from e
        except (telethon_errors.PhoneNumberInvalidError, ValueError) as e:
            logger.error(f"Invalid phone number format for {phone_number}: {e}", exc_info=True)
            raise TelegramAuthError(f"Invalid phone number format: {phone_number}") from e
        except Exception as e:
            logger.error(f"Error requesting Telegram code for {phone_number}: {e}", exc_info=True)
            raise TelegramGenericError(f"Failed to request Telegram code: {str(e)}") from e
        finally:
            if client and client.is_connected():
                logger.debug(f"Disconnecting client after code request for {phone_number}.")
                await client.disconnect()

    async def submit_login_code(
            self,
            phone_number: str,
            code: str,
            phone_code_hash: str,
            temporary_session_string: str,
    ) -> Dict[str, Any]:
        logger.info(f"Submitting Telegram login code for phone: {phone_number}")
        # Use the temporary session string associated with this specific login attempt
        client = await self._create_client(session_string=temporary_session_string)
        try:
            logger.debug(f"Connecting client for code submission for {phone_number}...")
            await client.connect()
            if not client.is_connected():
                raise TelegramConnectionError("Failed to connect to Telegram for code submission.")

            logger.debug(f"Signing in with code for {phone_number}...")
            signed_in_user = await client.sign_in(  # Use TelethonUserType for hint
                phone=phone_number,
                phone_code_hash=phone_code_hash,
                code=code,
            )
            # If 2FA is needed, client.sign_in will raise SessionPasswordNeededError
            # You would catch this and prompt the user for password, then call client.sign_in(password=...)
            logger.info(
                f"Successfully signed in for {phone_number}. User ID: {signed_in_user.id if signed_in_user else 'N/A'}")

            final_session_string = client.session.save()  # This is the authenticated session
            me = await client.get_me()  # Should be same as signed_in_user
            telegram_user_id = str(me.id) if me else None
            username = me.username if me else None

            if not telegram_user_id:
                # This should not happen if sign_in was successful
                raise TelegramAuthError("Failed to retrieve user details (Telegram User ID) after sign-in.")
            return {
                "final_session_string": final_session_string,
                "telegram_user_id": telegram_user_id,
                "username": username
            }
        except telethon_errors.SessionPasswordNeededError as e:
            logger.warning(f"2FA password needed for {phone_number}: {e}", exc_info=True)
            raise TelegramAuthError(f"Two-factor authentication password is required for {phone_number}.") from e
        except (telethon_errors.PhoneCodeInvalidError, telethon_errors.PhoneCodeExpiredError) as e:
            logger.warning(f"Invalid or expired code for {phone_number}: {e}", exc_info=True)
            raise TelegramAuthError(f"The code provided is invalid or has expired for {phone_number}.") from e
        except Exception as e:
            logger.error(f"Error submitting Telegram code for {phone_number}: {e}", exc_info=True)
            raise TelegramGenericError(f"Failed to submit Telegram code: {str(e)}") from e
        finally:
            if client and client.is_connected():
                logger.debug(f"Disconnecting client after code submission for {phone_number}.")
                await client.disconnect()


    async def get_me(self, session_string: str) -> Optional[Dict[str, Any]]:
        logger.debug(f"Getting 'me' for session: ...{session_string[-10:] if session_string else 'None'}")
        client = await self._create_client(session_string=session_string)
        try:
            await client.connect()
            if not client.is_connected() or not await client.is_user_authorized():
                logger.warning("Client not connected or authorized for get_me with provided session.")
                return None
            me = await client.get_me()
            if me:
                return {
                    "id": str(me.id), "username": me.username, "phone": me.phone,
                    "first_name": me.first_name, "last_name": me.last_name
                }
            return None
        except Exception as e:
            logger.error(f"Error in get_me: {e}", exc_info=True)
            return None
        finally:
            if client and client.is_connected():
                await client.disconnect()


    async def is_user_authorized(self, session_string: str) -> bool:
        client = await self._create_client(session_string=session_string)
        try:
            await client.connect()
            is_auth = await client.is_user_authorized()
            logger.debug(f"Session authorization check result: {is_auth}")
            return is_auth
        except Exception:
            return False
        finally:
            if client and client.is_connected():
                await client.disconnect()

    async def start_message_listener(
            self,
            service_uid: UUID,  # Key for this specific listener instance
            session_string: str,
            bot_uid: UUID,  # The parent bot this service belongs to (for context/logging)
            event_handler_service: TelegramEventHandlerService
    ) -> asyncio.Task:  # Return the asyncio.Task
        global _active_listener_tasks, _active_clients  # Now keyed by service_uid

        logger.info(
            f"Attempting to start message listener for service_uid: {service_uid} (Bot UID Context: {bot_uid})")

        # Check if a listener for this specific service_uid is already running
        if service_uid in _active_listener_tasks and not _active_listener_tasks[service_uid].done():
            logger.warning(f"Listener task already running for service_uid: {service_uid}. Stopping old one first.")
            await self.stop_message_listener(service_uid)  # Stop by service_uid

        logger.debug(f"Before starting, active listener tasks: {list(_active_listener_tasks.keys())}")
        logger.debug(f"Before starting, active clients: {list(_active_clients.keys())}")
        # Create a new client instance for this service_uid
        # _create_client should return a fresh client or one uniquely identified if pooling is complex
        client = await self._create_client(session_string=session_string)

        try:
            logger.debug(f"Connecting client for listener (service_uid: {service_uid})...")
            await client.connect()
            if not await client.is_user_authorized():
                logger.error(f"Cannot start listener for service_uid {service_uid}: Client not authorized.")
                await client.disconnect()
                raise TelegramAuthError("Client not authorized to start listener.")
            logger.debug(f"Client connected and authorized for listener (service_uid: {service_uid}).")

            # Handlers are attached to this specific client instance, now associated with service_uid
            # The previous check getattr(client, "_event_handlers_attached_for_bot_uid")
            # can be changed to reflect service_uid if needed, though a new client instance usually
            # doesn't have old handlers. For safety, explicitly removing and re-adding is robust.

            client.remove_event_handler(None,
                                        events.NewMessage)  # Clear any existing NewMessage handlers on this client instance

            @client.on(events.NewMessage(incoming=True))
            async def new_message_handler_wrapper(event):
                logger.debug(
                    f"Telethon event ID {event.id} received for service_uid {service_uid} (Bot UID Context: {bot_uid}) via client {id(client)}")
                # Pass service_uid and bot_uid_for_context to the event handler for full context
                await event_handler_service.handle_new_telethon_message(event, client, bot_uid, service_uid)

            logger.debug(f"Event handlers attached for service_uid {service_uid} to client {id(client)}")

            # Store client and task using service_uid as the key
            _active_clients[service_uid] = client

            async def listener_task_wrapper(client_instance: TelegramClient, current_service_uid: UUID,
                                            current_bot_uid_context: UUID):
                try:
                    logger.info(
                        f"Telethon client listener task starting for service_uid: {current_service_uid} (Bot UID Context: {current_bot_uid_context})")
                    await client_instance.run_until_disconnected()
                except asyncio.CancelledError:
                    logger.info(f"Telethon client listener task cancelled for service_uid: {current_service_uid}")
                except Exception as e_run:
                    logger.error(f"Telethon client listener for service_uid {current_service_uid} crashed: {e_run}",
                                 exc_info=True)
                finally:
                    logger.info(
                        f"Telethon client listener task finished for service_uid: {current_service_uid}. Cleaning up.")
                    if client_instance and client_instance.is_connected():
                        try:
                            await client_instance.disconnect()
                            logger.debug(
                                f"Client for service_uid {current_service_uid} disconnected in listener finally block.")
                        except Exception as disconn_e:
                            logger.error(
                                f"Error disconnecting client for service_uid {current_service_uid} in listener finally block: {disconn_e}")

                    # Clean up from global dicts using service_uid
                    _active_clients.pop(current_service_uid, None)
                    _active_listener_tasks.pop(current_service_uid, None)
                    logger.debug(
                        f"Cleaned up task and client for service_uid {current_service_uid} from global tracking.")

            task = asyncio.create_task(listener_task_wrapper(client, service_uid, bot_uid))
            _active_listener_tasks[service_uid] = task
            logger.info(f"Message listener task created and started for service_uid: {service_uid}")
            return task

        except Exception as e:
            logger.error(f"Failed to start message listener for service_uid {service_uid}: {e}", exc_info=True)
            if client and client.is_connected():
                await client.disconnect()
            _active_clients.pop(service_uid, None)  # Clean up if start failed
            _active_listener_tasks.pop(service_uid, None)  # Clean up if start failed
            raise TelegramGenericError(f"Could not start listener for service {service_uid}: {str(e)}") from e

    async def stop_message_listener(self, service_uid: UUID) -> None:  # Changed parameter name for clarity
        global _active_listener_tasks, _active_clients  # Now keyed by service_uid
        logger.info(f"Attempting to stop message listener for service_uid: {service_uid}")

        task_to_cancel = _active_listener_tasks.pop(service_uid, None)
        client_to_disconnect = _active_clients.pop(service_uid, None)

        if task_to_cancel and not task_to_cancel.done():
            logger.debug(f"Cancelling listener task for service_uid: {service_uid}")
            task_to_cancel.cancel()
            try:
                await task_to_cancel
            except asyncio.CancelledError:
                logger.info(f"Listener task for service_uid {service_uid} successfully cancelled.")
            except Exception as e:
                logger.error(f"Error awaiting cancelled task for service_uid {service_uid}: {e}", exc_info=True)
        elif task_to_cancel:  # Task existed but was already done
            logger.debug(f"Listener task for service_uid {service_uid} was already done.")
        else:  # No task found for this service_uid
            logger.warning(f"No active listener task found to stop for service_uid: {service_uid}")

        if client_to_disconnect and client_to_disconnect.is_connected():
            logger.debug(f"Disconnecting client for service_uid: {service_uid}")
            try:
                await client_to_disconnect.disconnect()
                logger.info(f"Client for service_uid {service_uid} disconnected.")
            except Exception as e:
                logger.error(f"Error disconnecting client for service_uid {service_uid}: {e}", exc_info=True)
        elif client_to_disconnect:  # Client existed but was already disconnected
            logger.debug(f"Client for service_uid {service_uid} was already disconnected.")
        else:  # No client found for this service_uid
            logger.debug(f"No active client instance found to disconnect for service_uid: {service_uid}")

        logger.info(f"Stop message listener process completed for service_uid: {service_uid}")



