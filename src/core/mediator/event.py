from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Callable, Dict, List

from src.core.base.event import ER, ET, BaseEventHandler

from src.core.base.event import BaseEvent


@dataclass(eq=False)
class EventMediator(ABC):
    _event_providers: Dict[ET, List[Callable[[], BaseEventHandler]]] = field(
        default_factory=lambda: defaultdict(list)
    )

    @abstractmethod
    def register_event_handlers(
        self,
        event_type: ET,
        providers: Iterable[Callable[[], BaseEventHandler]]
    ) -> None:
        pass

    @abstractmethod
    async def publish(self, events: Iterable[BaseEvent]) -> list[ER]:
        pass