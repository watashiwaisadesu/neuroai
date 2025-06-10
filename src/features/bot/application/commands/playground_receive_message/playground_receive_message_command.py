from dataclasses import dataclass
from uuid import UUID

from fastapi import WebSocket

from src.core.mediator.command import BaseCommand
from src.features.bot.domain.entities.bot_entity import BotEntity  # Import BotEntity


@dataclass
class PlaygroundReceiveMessageCommand(BaseCommand):
    """
    Command dispatched when a message is received from the bot playground WebSocket.
    """
    bot_uid: UUID
    user_uid: UUID
    websocket: WebSocket
    message_content: str
    target_bot_entity: BotEntity # Add the resolved BotEntity