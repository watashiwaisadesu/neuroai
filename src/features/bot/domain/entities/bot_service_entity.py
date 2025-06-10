from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from src.core.models.base_entity import BaseEntity


class BotServiceEntity(BaseEntity):
    bot_uid: UUID
    platform: str
    status: str
    linked_account_uid: Optional[UUID]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    service_details: Optional[Dict[str, Any]]


    def __init__(
        self,
        uid: UUID | None = None,
        bot_uid: UUID | None = None,
        platform: str = "",
        status: str = "reserved",
        linked_account_uid: Optional[UUID] = None,
        service_details: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        super().__init__(uid=uid)
        self.bot_uid = bot_uid
        self.platform = platform
        self.status = status
        self.linked_account_uid = linked_account_uid
        self.service_details = service_details if service_details is not None else {}  # <<< INITIALIZE (default to empty dict)

        if created_at:
            self.created_at = created_at
        if updated_at:
            self.updated_at = updated_at
