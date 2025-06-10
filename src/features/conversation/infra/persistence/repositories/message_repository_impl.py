# src/features/chat/infra/persistence/repositories/message_repository_impl.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import List, Optional
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.features.conversation.domain.entities.message_entity import MessageEntity
from src.features.conversation.domain.repositories.message_repository import IMessageRepository
from src.features.conversation.infra.persistence.models.message import MessageORM
from src.features.conversation.infra.mappers.message_mapper import MessageMapper




class MessageRepositoryImpl(IMessageRepository):
    """Concrete implementation of the IMessageRepository using SQLAlchemy."""

    def __init__(self, session: AsyncSession, mapper: MessageMapper):
        self._session = session
        self._mapper = mapper
        logger.debug("MessageRepositoryImpl initialized.")

    async def create(self, entity: MessageEntity, conversation_uid: UUID) -> MessageEntity:
        """Creates a new Message record associated with a conversation."""
        logger.debug(f"Creating message {entity.uid} for conversation {conversation_uid}")

        orm_obj = self._mapper.from_entity(entity)
        if not orm_obj:
            raise ValueError("Failed to map MessageEntity to ORM object.")

        # Associate with the conversation
        orm_obj.conversation_uid = conversation_uid

        self._session.add(orm_obj)
        try:
            await self._session.flush()
            await self._session.refresh(orm_obj)
            logger.info(f"Successfully created message {orm_obj.uid} for conversation {conversation_uid}")
            return self._mapper.to_entity(orm_obj)
        except IntegrityError as e:
            logger.error(f"IntegrityError creating message {entity.uid}: {e}", exc_info=True)
            await self._session.rollback()
            raise
        except Exception as e:
            logger.error(f"Error creating message {entity.uid}: {e}", exc_info=True)
            await self._session.rollback()
            raise

    async def update(self, entity: MessageEntity) -> MessageEntity:
        """Updates an existing Message record."""
        logger.debug(f"Updating message {entity.uid}")

        existing_orm = await self._session.get(MessageORM, entity.uid)
        if not existing_orm:
            logger.warning(f"Message not found for update with UID: {entity.uid}")
            raise ValueError(f"Message with UID {entity.uid} not found.")

        # Update attributes - be careful about what should be updatable
        updated = False
        if existing_orm.role != entity.role.value:  # Assuming role is stored as string in DB
            existing_orm.role = entity.role.value
            updated = True
        if existing_orm.content != entity.content:
            existing_orm.content = entity.content
            updated = True
        if existing_orm.timestamp != entity.timestamp:
            existing_orm.timestamp = entity.timestamp
            updated = True

        if not updated:
            logger.debug(f"No updatable changes detected for message UID {entity.uid}.")
            return entity

        try:
            await self._session.flush()
            await self._session.refresh(existing_orm)
            logger.info(f"Successfully updated message {existing_orm.uid}")
            return self._mapper.to_entity(existing_orm)
        except Exception as e:
            logger.error(f"Error updating message {entity.uid}: {e}", exc_info=True)
            await self._session.rollback()
            raise

    async def get(self, uid: UUID) -> Optional[MessageEntity]:
        """Retrieves a Message by its UID."""
        logger.debug(f"Finding message by UID: {uid}")

        try:
            orm_obj = await self._session.get(MessageORM, uid)
            if not orm_obj:
                logger.debug(f"Message not found by UID: {uid}")
                return None
            return self._mapper.to_entity(orm_obj)
        except Exception as e:
            logger.error(f"Error finding message by UID {uid}: {e}", exc_info=True)
            return None

    async def delete_by_uid(self, uid: UUID) -> None:
        """Deletes a message by its unique identifier."""
        logger.debug(f"Attempting to delete message by UID: {uid}")

        orm_obj = await self._session.get(MessageORM, uid)
        if not orm_obj:
            logger.warning(f"Message not found for deletion by UID: {uid}")
            raise ValueError(f"Message with UID {uid} not found.")

        try:
            await self._session.delete(orm_obj)
            await self._session.flush()
            logger.info(f"Successfully deleted message with UID: {uid}")
        except Exception as e:
            logger.error(f"Error deleting message by UID {uid}: {e}", exc_info=True)
            await self._session.rollback()
            raise

    async def find_by_conversation_uid(self, conversation_uid: UUID) -> List[MessageEntity]:
        """Finds all messages associated with a given conversation UID."""
        logger.debug(f"Finding messages for conversation UID: {conversation_uid}")

        try:
            stmt = (
                select(MessageORM)
                .where(MessageORM.conversation_uid == conversation_uid)
                .order_by(MessageORM.timestamp)
            )
            result = await self._session.execute(stmt)
            orm_objects = result.scalars().all()

            entities = [self._mapper.to_entity(orm) for orm in orm_objects]
            logger.debug(f"Found {len(entities)} messages for conversation {conversation_uid}")
            return entities
        except Exception as e:
            logger.error(f"Error finding messages for conversation {conversation_uid}: {e}", exc_info=True)
            return []

    async def find_latest_by_conversation_uid(self, conversation_uid: UUID, limit: int = 10) -> List[MessageEntity]:
        """Finds the latest N messages for a conversation."""
        logger.debug(f"Finding latest {limit} messages for conversation UID: {conversation_uid}")

        try:
            stmt = (
                select(MessageORM)
                .where(MessageORM.conversation_uid == conversation_uid)
                .order_by(MessageORM.timestamp.desc())
                .limit(limit)
            )
            result = await self._session.execute(stmt)
            orm_objects = result.scalars().all()

            # Reverse to get chronological order
            entities = [self._mapper.to_entity(orm) for orm in reversed(orm_objects)]
            logger.debug(f"Found {len(entities)} latest messages for conversation {conversation_uid}")
            return entities
        except Exception as e:
            logger.error(f"Error finding latest messages for conversation {conversation_uid}: {e}", exc_info=True)
            return []