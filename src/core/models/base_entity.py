from dataclasses import dataclass, field
from typing import List
from uuid import UUID, uuid4
from abc import ABC
from src.infra.logging.setup_async_logging import async_logger as logger
from copy import copy

from src.core.base.event import BaseEvent
from src.core.models.mixins import TimestampMixin



@dataclass(eq=False)
class BaseEntity(TimestampMixin, ABC):
    uid: UUID = field(default_factory=uuid4, kw_only=True)
    # created_at and updated_at are assumed to be provided by TimestampMixin.
    # If TimestampMixin makes them dataclass fields, they will be part of __init__.
    # If not, ensure TimestampMixin.__init__ or other mechanisms set them.

    _events: List[BaseEvent] = field(default_factory=list, repr=False, init=False)

    def __post_init__(self):
        # This will be called after fields (uid) from this class AND
        # fields from TimestampMixin (if it's a dataclass providing fields) are initialized.
        # Ensure self.created_at exists from TimestampMixin before logging.
        # If TimestampMixin is not a dataclass and needs explicit super() call, it's more complex.
        # Assuming TimestampMixin sets created_at upon initialization.
        log_created_at = getattr(self, 'created_at', 'N/A (TimestampMixin pending)')
        logger.debug(f"BaseEntity initialized/accessed. UID: {self.uid}, Created: {log_created_at}")


    def add_event(self, event: BaseEvent) -> None:
        self._events.append(event)
        logger.debug(f"Event {event.__class__.__name__} added to entity UID {self.uid}")


    def pull_events(self) -> List[BaseEvent]:
        pulled_events = copy(self._events)
        self._events.clear()
        logger.debug(f"Pulled {len(pulled_events)} events from entity UID {self.uid}")
        return pulled_events

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseEntity): # Or type(self) is type(other)
            return NotImplemented
        return self.uid == other.uid

    def __hash__(self) -> int:
        return hash(self.uid)
