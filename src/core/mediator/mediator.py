import asyncio
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Callable

from src.core.base.command import CR, CT, BaseCommand, BaseCommandHandler
from src.core.base.event import ER, ET, BaseEventHandler, BaseEvent
from src.core.base.query import BaseQueryHandler, QT, BaseQuery, QR
from src.core.exceptions.mediator import (
    CommandHandlersNotRegisteredException,
    EventHandlersNotRegisteredException,
    CommandAlreadyRegisteredException, QueryAlreadyRegisteredException, QueryHandlersNotRegisteredException
)

from src.core.mediator.command import CommandMediator
from src.core.mediator.event import EventMediator
from src.core.mediator.query import QueryMediator


@dataclass(eq=False)
class Mediator(CommandMediator, EventMediator, QueryMediator):
    def register_command_handler(
        self,
        command_type: CT,
        provider: Callable[[], BaseCommandHandler]
    ) -> None:
        if command_type in self._command_providers:
            raise CommandAlreadyRegisteredException(command_type)
        self._command_providers[command_type] = provider

    async def execute(self, command: BaseCommand) -> CR:
        provider = self._command_providers.get(type(command))
        if not provider:
            raise CommandHandlersNotRegisteredException(type(command))
        handler = provider()
        return await handler(command)

    # Query methods
    def register_query_handler(
            self,
            query_type: QT,
            provider: Callable[[], BaseQueryHandler]
    ) -> None:
        if query_type in self._query_providers:
            raise QueryAlreadyRegisteredException(query_type)
        self._query_providers[query_type] = provider

    async def query(self, query: BaseQuery) -> QR:
        provider = self._query_providers.get(type(query))
        if not provider:
            raise QueryHandlersNotRegisteredException(type(query))
        handler = provider()
        return await handler(query)

    def register_event_handlers(
        self,
        event_type: ET,
        providers: Iterable[Callable[[], BaseEventHandler]]
    ) -> None:
        """
        Registers multiple handlers for a specific event type.
        Event handlers are stored as callables that return an instance of BaseEventHandler.
        """
        # Ensure the list for the event type exists before extending
        if event_type not in self._event_providers:
            self._event_providers[event_type] = []
        self._event_providers[event_type].extend(providers)

    async def publish(self, events: Iterable[BaseEvent]) -> list[ER]:
        results: list[ER] = []
        for event in events:
            providers = self._event_providers.get(type(event), [])
            if not providers:
                raise EventHandlersNotRegisteredException()
            for provider in providers:
                handler = provider()
                asyncio.create_task(handler.handle(event))
        return []