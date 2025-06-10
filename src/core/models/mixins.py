from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass(kw_only=True) # Good practice for base/mixin classes
class TimestampMixin:
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def update_timestamp(self):
        self.updated_at = datetime.now(timezone.utc)



