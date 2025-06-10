# src/core/exceptions/mediator.py
from typing import Type
from src.core.base.command import BaseCommand
from src.core.base.event import BaseEvent


class MediatorException(Exception):
    """Base exception for mediator-related errors"""
    pass


class CommandHandlersNotRegisteredException(MediatorException):
    """Raised when no command handler is registered for a command type"""

    def __init__(self, command_type: Type[BaseCommand]):
        self.command_type = command_type
        super().__init__(f"No command handler registered for command type: {command_type.__name__}")

    def __str__(self) -> str:
        return f"No command handler registered for command type: {self.command_type.__name__}"


class EventHandlersNotRegisteredException(MediatorException):
    """Raised when no event handler is registered for an event type"""

    def __init__(self, event_type: Type[BaseEvent] = None):
        self.event_type = event_type
        if event_type:
            message = f"No event handler registered for event type: {event_type.__name__}"
        else:
            message = "No event handlers registered for the given event type"
        super().__init__(message)

    def __str__(self) -> str:
        if self.event_type:
            return f"No event handler registered for event type: {self.event_type.__name__}"
        return "No event handlers registered for the given event type"


class CommandAlreadyRegisteredException(MediatorException):
    """Raised when trying to register a command handler that's already registered"""

    def __init__(self, command_type: Type[BaseCommand]):
        self.command_type = command_type
        super().__init__(f"Command handler already registered for command type: {command_type.__name__}")

    def __str__(self) -> str:
        return f"Command handler already registered for command type: {self.command_type.__name__}"


class QueryHandlersNotRegisteredException(Exception):
    def __init__(self, query_type: type = None):
        self.query_type = query_type
        super().__init__(f"No query handler registered for {query_type}")


class QueryAlreadyRegisteredException(Exception):
    def __init__(self, query_type: type):
        self.query_type = query_type
        super().__init__(f"Query handler already registered for {query_type}")