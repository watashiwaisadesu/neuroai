# src/features/bot/application/commands/handle_playground_connection/handle_playground_connection_handler.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass

from fastapi import WebSocketDisconnect, HTTPException, status # Import HTTPException and status
from fastapi.websockets import WebSocketState

from src.core.mediator.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.features.bot.application.commands.handle_playground_connection.handle_playground_connection_command import \
    HandlePlaygroundConnectionCommand
from src.features.bot.application.commands.playground_receive_message.playground_receive_message_command import \
    PlaygroundReceiveMessageCommand

from src.features.bot.application.services.bot_access_service import BotAccessService # Import BotAccessService
from src.features.bot.domain.entities.bot_entity import BotEntity # Import BotEntity




@dataclass
class HandlePlaygroundConnectionCommandHandler(
    BaseCommandHandler[HandlePlaygroundConnectionCommand, None]
):
    _mediator: Mediator
    _bot_access_service: BotAccessService # Inject BotAccessService

    async def __call__(self, command: HandlePlaygroundConnectionCommand) -> None:
        websocket = command.websocket
        bot_uid = command.bot_uid
        current_user = command.current_user
        target_bot: BotEntity = None # Initialize target_bot

        try:
            # Perform bot access check
            # Define allowed roles for playground access
            allowed_roles = ["editor", "admin", "owner"]
            target_bot = await self._bot_access_service.check_single_bot_access(
                user_uid=current_user.uid,
                bot_uid=bot_uid,
                allowed_roles=allowed_roles
            )
            logger.info(f"Access granted for user {current_user.uid} to bot {bot_uid} in playground.")

            await websocket.accept()
            logger.info(f"WebSocket connection accepted for bot {bot_uid} by user {current_user.uid} in playground.")

            while True:
                try:
                    user_message_text = await websocket.receive_text()
                    logger.info(
                        f"Received playground message for bot {bot_uid} from user {current_user.uid}: '{user_message_text}'"
                    )

                    # Dispatch a command to process the incoming message, passing the resolved BotEntity
                    receive_command = PlaygroundReceiveMessageCommand(
                        bot_uid=target_bot.uid, # Use target_bot.uid
                        user_uid=current_user.uid,
                        websocket=websocket,
                        message_content=user_message_text,
                        target_bot_entity=target_bot # Pass the resolved BotEntity
                    )
                    await self._mediator.execute(receive_command)

                except WebSocketDisconnect:
                    logger.info(
                        f"WebSocket disconnected for bot {bot_uid} by user {current_user.uid} in playground."
                    )
                    break
                except Exception as e:
                    logger.error(
                        f"Error during WebSocket message reception for bot {bot_uid}: {e}",
                        exc_info=True,
                    )
                    try:
                        if websocket.client_state != WebSocketState.DISCONNECTED:
                            await websocket.send_text(f"Error receiving message: {str(e)}")
                    except RuntimeError:
                        logger.debug(
                            "Socket already closed when trying to send reception error."
                        )
                    break

        except HTTPException as http_exc:
            # If access is denied (e.g., 403 Forbidden from check_single_bot_access)
            logger.warning(f"WebSocket connection denied for bot {bot_uid} by user {current_user.uid}: {http_exc.detail}")
            close_code = status.WS_1008_POLICY_VIOLATION # Standard code for policy violation
            if http_exc.status_code == status.HTTP_401_UNAUTHORIZED:
                close_code = status.WS_1008_POLICY_VIOLATION # Or 1008 for unauth if you prefer
            elif http_exc.status_code == status.HTTP_403_FORBIDDEN:
                close_code = status.WS_1008_POLICY_VIOLATION # Policy violation
            elif http_exc.status_code == status.HTTP_404_NOT_FOUND:
                close_code = status.WS_1008_POLICY_VIOLATION # Or 1008 if bot not found by user
            try:
                if websocket.client_state != WebSocketState.DISCONNECTED:
                    await websocket.close(code=close_code, reason=http_exc.detail)
            except RuntimeError:
                logger.debug("Socket already closed during access denial cleanup.")
        except Exception as e:
            logger.error(
                f"Overall WebSocket error for bot {bot_uid} with user {current_user.uid} in playground: {e}",
                exc_info=True,
            )
            try:
                if websocket.client_state != WebSocketState.DISCONNECTED:
                    await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason=f"An unexpected error occurred: {str(e)}")
            except RuntimeError:
                logger.debug("Socket already closed when trying to send final error.")
        finally:
            logger.info(f"Closing WebSocket connection for bot {bot_uid}, user {current_user.uid}")
            try:
                 if websocket.client_state != WebSocketState.DISCONNECTED:
                     await websocket.close(code=status.WS_1000_NORMAL_CLOSURE) # Normal closure
            except RuntimeError:
                 logger.debug("Socket already closed during final cleanup.")
            except Exception as close_exc:
                 logger.error(f"Error during WebSocket final close for bot {bot_uid}: {close_exc}", exc_info=True)