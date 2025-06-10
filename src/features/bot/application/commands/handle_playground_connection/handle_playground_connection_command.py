from dataclasses import dataclass
from uuid import UUID

from fastapi import WebSocket

from src.core.mediator.command import BaseCommand
from src.features.identity.domain.entities.user_entity import UserEntity


@dataclass
class HandlePlaygroundConnectionCommand(BaseCommand):
    """
    Command to initiate and manage the lifecycle of a bot playground WebSocket connection.
    Its handler will accept the connection and set up listeners, dispatching
    further commands for message processing.
    """
    websocket: WebSocket
    bot_uid: UUID
    current_user: UserEntity