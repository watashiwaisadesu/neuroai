from dataclasses import dataclass

from fastapi import WebSocket

from src.core.mediator.command import BaseCommand


@dataclass
class PlaygroundSendMessageCommand(BaseCommand):
    """
    Command dispatched to send a message back to the bot playground WebSocket.
    """
    websocket: WebSocket
    message_content: str