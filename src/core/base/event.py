from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TypeVar, Any, Generic
from uuid import uuid4, UUID


@dataclass(frozen=True)
class BaseEvent(ABC):
    event_id: UUID = field(default_factory=uuid4, kw_only=True)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc), kw_only=True)

ET = TypeVar("ET", bound=BaseEvent)
ER = TypeVar("ER", bound=Any)


@dataclass
class BaseEventHandler(ABC, Generic[ET, ER]):
    # message_broker: BaseMessageBroker
    # connection_manager: ConnectionManager
    topic: str | None = None

    @abstractmethod
    async def handle(self, event: ET) -> ER:
        pass