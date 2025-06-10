# src/features/bot/application/commands/playground_send_message/playground_send_message_handler.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass

from fastapi.websockets import WebSocketState

from src.core.mediator.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.features.bot.application.commands.playground_send_message.playground_send_message_command import \
    PlaygroundSendMessageCommand




@dataclass
class PlaygroundSendMessageCommandHandler(
    BaseCommandHandler[PlaygroundSendMessageCommand, None]
):
    _mediator: Mediator
    async def __call__(self, command: PlaygroundSendMessageCommand) -> None:
        logger.info(f"Attempting to send message to playground WebSocket: '{command.message_content[:50]}...'")
        try:
            if command.websocket.client_state != WebSocketState.DISCONNECTED:
                await command.websocket.send_text(command.message_content)
                logger.debug("Message successfully sent to playground WebSocket.")
            else:
                logger.warning("Attempted to send message to a disconnected playground WebSocket.")
        except RuntimeError:
            logger.warning("RuntimeError: Playground WebSocket already closed when trying to send message.")
        except Exception as e:
            logger.error(f"Failed to send message to playground WebSocket: {e}", exc_info=True)