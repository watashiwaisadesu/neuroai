# src/features/bot/api/routes/playground.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, WebSocket, status
from fastapi.websockets import WebSocketState

# Import Mediator
from src.core.mediator.mediator import Mediator  # Import the Mediator
# Import Command, DTOs, Entities, Dependencies
# Updated to import the new HandlePlaygroundConnectionCommand
from src.features.bot.application.commands.handle_playground_connection.handle_playground_connection_command import \
    HandlePlaygroundConnectionCommand
# Import API-specific dependencies
from src.features.identity.dependencies import get_current_user
from src.features.identity.domain.entities.user_entity import UserEntity


playground_router = APIRouter()

@playground_router.websocket("/playground/{bot_uid}")
@inject # Add inject for mediator
async def bot_playground_websocket(
    websocket: WebSocket,
    bot_uid: UUID,
    current_user: UserEntity = Depends(get_current_user),
    mediator: Mediator = Depends(Provide["mediator"]) # Inject mediator
):
    """
    Handles WebSocket connections for the bot playground.
    Authenticates user via Bearer token in the Authorization header.
    Uses Mediator to dispatch connection handling.
    """
    logger.info(f"Playground WebSocket: User {current_user.uid} connecting to bot {bot_uid}")

    connection_command = HandlePlaygroundConnectionCommand(
        websocket=websocket,
        bot_uid=bot_uid,
        current_user=current_user
    )

    try:
        await mediator.execute(connection_command)
    except Exception as e:
        logger.error(f"Unhandled exception during playground WebSocket setup/initialization for bot {bot_uid}: {e}", exc_info=True)
        # Ensure socket is closed on unhandled errors
        try:
            if websocket.client_state != WebSocketState.DISCONNECTED:
                await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except RuntimeError:
            pass # Socket already closed