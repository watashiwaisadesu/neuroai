from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Dict, Callable

from src.core.base.command import CR, CT, BaseCommand, BaseCommandHandler


@dataclass(eq=False)
class CommandMediator(ABC):
    _command_providers: Dict[CT, Callable[[], BaseCommandHandler]] = field(default_factory=dict)

    @abstractmethod
    def register_command_handler(
        self,
        command_type: CT,
        provider: Callable[[], BaseCommandHandler]
    ) -> None:
        pass

    @abstractmethod
    async def execute(self, command: BaseCommand) -> CR:
        pass