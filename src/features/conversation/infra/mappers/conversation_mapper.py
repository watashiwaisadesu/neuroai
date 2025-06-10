# src/features/chat/infra/mappers/conversation_mapper.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import Optional, Type, List

# Import domain/infra classes
from src.features.conversation.domain.entities.conversation_entity import ConversationEntity
from src.features.conversation.domain.entities.message_entity import MessageEntity
from src.features.conversation.domain.enums import ChatPlatform
from src.features.conversation.infra.persistence.models.conversation import ConversationORM
from src.features.conversation.infra.persistence.models.message import MessageORM
from src.features.conversation.domain.value_objects.participant_info import ParticipantInfo
# Import MessageMapper (defined below or in separate file)
from src.features.conversation.infra.mappers.message_mapper import MessageMapper # Adjust import path



class ConversationMapper:
    """Maps between ConversationEntity and ConversationORM."""

    entity_cls: Type[ConversationEntity]
    orm_cls: Type[ConversationORM]
    _message_mapper: MessageMapper # Inject or instantiate message mapper

    def __init__(self, entity_cls: Type[ConversationEntity], orm_cls: Type[ConversationORM]):
        self.entity_cls = entity_cls
        self.orm_cls = orm_cls
        # Instantiate message mapper (assuming it takes its classes too)
        self._message_mapper = MessageMapper(MessageEntity, MessageORM)
        logger.debug(f"ConversationMapper initialized for {entity_cls.__name__} and {orm_cls.__name__}")

    def to_entity(self, orm_obj: ConversationORM) -> Optional[ConversationEntity]:
        """Maps ORM object to Domain Entity."""
        if not orm_obj: return None
        logger.debug(f"Mapping ConversationORM (UID: {orm_obj.uid}) to Entity.")
        try:
            participant_info = ParticipantInfo(
                sender_id=orm_obj.sender_id,
                sender_number=orm_obj.sender_number,
                sender_nickname=orm_obj.sender_nickname
            )
            # Map messages using MessageMapper
            message_entities = [self._message_mapper.to_entity(msg_orm) for msg_orm in orm_obj.messages if msg_orm]

            entity = self.entity_cls(
                uid=orm_obj.uid,
                created_at=getattr(orm_obj, 'created_at', None),
                updated_at=getattr(orm_obj, 'updated_at', None),
                owner_uid=orm_obj.owner_uid,
                bot_uid=orm_obj.bot_uid,
                platform=ChatPlatform(orm_obj.platform), # Convert string to Enum
                participant=participant_info,
                bot_name=orm_obj.bot_name,
                crm_catalog_id=orm_obj.crm_catalog_id,
                initial_messages=message_entities # Pass mapped messages
            )
            return entity
        except Exception as e:
            logger.error(f"Error mapping ConversationORM to Entity (UID: {orm_obj.uid}): {e}", exc_info=True)
            raise

    def from_entity(self, entity: ConversationEntity) -> Optional[ConversationORM]:
        """Maps Domain Entity to ORM object."""
        if not entity: return None
        logger.debug(f"Mapping ConversationEntity (UID: {entity.uid}) to ORM.")
        try:
            orm_data = {
                "uid": entity.uid,
                "created_at": getattr(entity, 'created_at', None),
                "updated_at": getattr(entity, 'updated_at', None),
                "owner_uid": entity.owner_uid,
                "bot_uid": entity.bot_uid,
                "platform": entity.platform.value, # Convert Enum to string value
                "sender_id": entity.participant.sender_id,
                "sender_number": entity.participant.sender_number,
                "sender_nickname": entity.participant.sender_nickname,
                "bot_name": entity.bot_name,
                "crm_catalog_id": entity.crm_catalog_id,
                # Messages are usually handled via relationship, not direct mapping here
            }
            orm_instance = self.orm_cls(**orm_data)
            # Note: Mapping messages back might be needed for updates if not handled by session
            # orm_instance.messages = [self._message_mapper.from_entity(msg_ent) for msg_ent in entity.messages]
            return orm_instance
        except Exception as e:
            logger.error(f"Error mapping ConversationEntity to ORM (UID: {entity.uid}): {e}", exc_info=True)
            raise