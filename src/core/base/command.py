from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar, Any

from src.core.mediator.event import EventMediator


@dataclass
class BaseCommand(ABC):
    pass


CT = TypeVar('CT', bound=BaseCommand)
CR = TypeVar('CR', bound=Any)


@dataclass
class BaseCommandHandler(ABC, Generic[CT, CR]):
    _mediator: EventMediator

    @abstractmethod
    async def __call__(self, task: CT) -> CR:
        raise NotImplementedError()
