# src/features/integrations/telegram/infra/mappers/telegram_account_link_mapper.py (New file)

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import Optional, Type

from src.features.integrations.messengers.telegram.domain.entities.telegram_account_link_entity import TelegramAccountLinkEntity
from src.features.integrations.messengers.telegram.infra.persistence.models.telegram_account_link import TelegramAccountLinkORM




class TelegramAccountLinkMapper:
    entity_cls: Type[TelegramAccountLinkEntity]
    orm_cls: Type[TelegramAccountLinkORM]

    def __init__(self, entity_cls: Type[TelegramAccountLinkEntity], orm_cls: Type[TelegramAccountLinkORM]):
        self.entity_cls = entity_cls
        self.orm_cls = orm_cls

    def to_entity(self, orm_obj: TelegramAccountLinkORM) -> Optional[TelegramAccountLinkEntity]:
        if not orm_obj: return None
        return self.entity_cls(
            uid=orm_obj.uid,
            created_at=getattr(orm_obj, 'created_at', None),
            updated_at=getattr(orm_obj, 'updated_at', None),
            bot_uid=orm_obj.bot_uid,
            platform_user_uid=orm_obj.platform_user_uid,
            telegram_user_id=orm_obj.telegram_user_id,
            phone_number=orm_obj.phone_number,
            username=orm_obj.username,
            session_string=orm_obj.session_string,
            phone_code_hash=orm_obj.phone_code_hash,
            is_active=orm_obj.is_active,
            last_connected_at=orm_obj.last_connected_at
        )

    def from_entity(self, entity: TelegramAccountLinkEntity) -> Optional[TelegramAccountLinkORM]:
        if not entity: return None
        data = {
            "uid": entity.uid,
            # created_at, updated_at usually handled by DB/Base
            "bot_uid": entity.bot_uid,
            "platform_user_uid": entity.platform_user_uid,
            "telegram_user_id": entity.telegram_user_id,
            "phone_number": entity.phone_number,
            "username": entity.username,
            "session_string": entity.session_string,
            "phone_code_hash": entity.phone_code_hash,
            "is_active": entity.is_active,
            "last_connected_at": entity.last_connected_at
        }
        if entity.uid is None and "uid" in data: data.pop("uid")
        return self.orm_cls(**data)
