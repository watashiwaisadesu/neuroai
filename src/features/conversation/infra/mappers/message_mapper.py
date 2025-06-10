
# src/features/chat/infra/mappers/message_mapper.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import Optional, Type

# Import domain/infra classes
from src.features.conversation.domain.entities.message_entity import MessageEntity
from src.features.conversation.domain.enums import MessageRole
from src.features.conversation.infra.persistence.models.message import MessageORM



class MessageMapper:
    """Maps between MessageEntity and MessageORM."""

    entity_cls: Type[MessageEntity]
    orm_cls: Type[MessageORM]

    def __init__(self, entity_cls: Type[MessageEntity], orm_cls: Type[MessageORM]):
        self.entity_cls = entity_cls
        self.orm_cls = orm_cls
        logger.debug(f"MessageMapper initialized for {entity_cls.__name__} and {orm_cls.__name__}")

    def to_entity(self, orm_obj: MessageORM) -> Optional[MessageEntity]:
        """Maps ORM object to Domain Entity."""
        if not orm_obj: return None
        logger.debug(f"Mapping MessageORM (UID: {orm_obj.uid}) to Entity.")
        try:
            entity = self.entity_cls(
                uid=orm_obj.uid,
                created_at=getattr(orm_obj, 'created_at', None),
                updated_at=getattr(orm_obj, 'updated_at', None),
                # conversation_id=orm_obj.conversation_uid, # Not usually needed in entity if part of aggregate
                role=MessageRole(orm_obj.role), # Convert string to Enum
                content=orm_obj.content,
                timestamp=orm_obj.timestamp,
                tokens_user=orm_obj.tokens_user or 0,
                tokens_ai=orm_obj.tokens_ai or 0
            )
            return entity
        except Exception as e:
            logger.error(f"Error mapping MessageORM to Entity (UID: {orm_obj.uid}): {e}", exc_info=True)
            raise

    def from_entity(self, entity: MessageEntity) -> Optional[MessageORM]:
        """Maps Domain Entity to ORM object."""
        if not entity: return None
        logger.debug(f"Mapping MessageEntity (UID: {entity.uid}) to ORM.")
        try:
            orm_data = {
                "uid": entity.uid,
                "created_at": getattr(entity, 'created_at', None),
                "updated_at": getattr(entity, 'updated_at', None),
                # "conversation_uid": entity.conversation_id, # Set by relationship usually
                "role": entity.role.value, # Convert Enum to string value
                "content": entity.content,
                "timestamp": entity.timestamp,
                "tokens_user": entity.tokens_user,
                "tokens_ai": entity.tokens_ai,
            }
            orm_instance = self.orm_cls(**orm_data)
            return orm_instance
        except Exception as e:
            logger.error(f"Error mapping MessageEntity to ORM (UID: {entity.uid}): {e}", exc_info=True)
            raise
