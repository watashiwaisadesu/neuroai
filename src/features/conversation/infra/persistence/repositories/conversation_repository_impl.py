# src/features/chat/infra/persistence/repositories/conversation_repository_impl.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import List, Optional
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload  # Use selectinload for async relationships

from src.features.conversation.domain.entities.conversation_entity import ConversationEntity
from src.features.conversation.domain.enums import ChatPlatform
# Import domain interface and entity
from src.features.conversation.domain.repositories.conversation_repository import IConversationRepository
from src.features.conversation.infra.mappers.conversation_mapper import ConversationMapper  # Assuming this exists
# Import infrastructure components
from src.features.conversation.infra.persistence.models.conversation import ConversationORM

# Import custom exceptions if needed
# from src.features.chat.domain.exceptions.chat_exceptions import ConversationNotFoundError, ConversationCreationError



class ConversationRepositoryImpl(IConversationRepository):
    """Concrete implementation of the IConversationRepository using SQLAlchemy."""

    _session: AsyncSession
    _mapper: ConversationMapper

    def __init__(self, session: AsyncSession):
        self._session = session
        # Instantiate the specific mapper
        self._mapper = ConversationMapper(ConversationEntity, ConversationORM) # Pass classes if needed
        logger.debug("ConversationRepositoryImpl initialized.")

    # --- BaseRepository Method Implementations ---

    async def create(self, entity: ConversationEntity) -> ConversationEntity:
        """Creates a new Conversation record."""
        orm_obj = self._mapper.from_entity(entity)
        if not orm_obj:
             raise ValueError("Failed to map ConversationEntity to ORM object.")

        logger.debug(f"Adding Conversation ORM object to session (UID: {entity.uid})")
        self._session.add(orm_obj)
        try:
            await self._session.flush()
            # Refresh to get DB defaults like created_at/updated_at
            await self._session.refresh(orm_obj)
            logger.info(f"Successfully flushed creation for Conversation UID: {orm_obj.uid}")
            # Map back the refreshed state, including potentially loaded messages if needed
            # The mapper should handle mapping messages if the relationship loaded them
            return self._mapper.to_entity(orm_obj)
        except IntegrityError as e:
            logger.error(f"IntegrityError creating Conversation (UID: {entity.uid}): {e}", exc_info=True)
            await self._session.rollback()
            raise # Re-raise specific exception like ConversationCreationError(str(e)) from e
        except Exception as e:
            logger.error(f"Error during Conversation creation flush (UID: {entity.uid}): {e}", exc_info=True)
            await self._session.rollback()
            raise

    async def update(self, entity: ConversationEntity) -> ConversationEntity:
        """Updates an existing conversation."""
        logger.debug(f"Attempting to update Conversation with UID: {entity.uid}")
        existing_orm = await self._session.get(ConversationORM, entity.uid)
        if not existing_orm:
            logger.warning(f"Conversation not found for update with UID: {entity.uid}")
            raise ValueError(f"Conversation with UID {entity.uid} not found.") # Or ConversationNotFoundError

        # Update attributes - be careful about what should be updatable
        updated = False
        if existing_orm.crm_catalog_id != entity.crm_catalog_id:
             existing_orm.crm_catalog_id = entity.crm_catalog_id
             updated = True

        if hasattr(entity, 'updated_at') and entity.updated_at:
            existing_orm.updated_at = entity.updated_at
            updated = True

            # Update bot_name if it changed
        if hasattr(existing_orm, 'bot_name') and existing_orm.bot_name != entity.bot_name:
            existing_orm.bot_name = entity.bot_name
            updated = True
        # Add other updatable fields (e.g., bot_name if it can change)

        # Note: Updating messages typically happens via adding/removing MessageEntities
        # and relying on the ORM relationship cascade/management, not directly here.

        if not updated:
             logger.debug(f"No updatable changes detected for conversation UID {entity.uid}.")
             return entity # Return original if no changes

        try:
            await self._session.flush()
            await self._session.refresh(existing_orm)
            logger.info(f"Successfully flushed update for Conversation UID: {existing_orm.uid}")
            return self._mapper.to_entity(existing_orm)
        except Exception as e:
            logger.error(f"Error during Conversation update (UID: {entity.uid}): {e}", exc_info=True)
            await self._session.rollback()
            raise

    async def delete_by_uid(self, uid: UUID) -> None:
        """Deletes a conversation by its unique identifier."""
        logger.debug(f"Attempting to delete conversation by UID: {uid}")
        orm_obj = await self._session.get(ConversationORM, uid)
        if not orm_obj:
            logger.warning(f"Conversation not found for deletion by UID: {uid}")
            raise ValueError(f"Conversation with UID {uid} not found.") # Or ConversationNotFoundError
        try:
            await self._session.delete(orm_obj)
            await self._session.flush()
            logger.info(f"Successfully deleted conversation with UID: {uid}")
        except Exception as e:
            logger.error(f"Error deleting conversation by UID {uid}: {e}", exc_info=True)
            await self._session.rollback()
            raise

    async def find_by_uid(self, uid: UUID, load_messages: bool = False) -> Optional[ConversationEntity]:
        """Finds a conversation entry by its unique identifier."""
        logger.debug(f"Finding conversation by UID: {uid}, Load messages: {load_messages}")
        statement = select(ConversationORM)
        if load_messages:
             # Use selectinload for efficient loading of the messages collection
             statement = statement.options(selectinload(ConversationORM.messages))
        statement = statement.where(ConversationORM.uid == uid)

        try:
            result = await self._session.execute(statement)
            orm_obj = result.scalar_one_or_none()
            if not orm_obj:
                 logger.debug(f"Conversation not found by UID: {uid}")
                 return None
            return self._mapper.to_entity(orm_obj) # Mapper handles included messages
        except Exception as e:
            logger.error(f"Error finding conversation by UID {uid}: {e}", exc_info=True)
            return None

    # --- Specific Method Implementations ---

    async def find_by_bot_uids(
        self,
        bot_uids: List[UUID],
        load_messages: bool = False
        ) -> List[ConversationEntity]:
        """Finds all conversations associated with the given bot UIDs."""
        if not bot_uids: return []
        logger.debug(f"Finding conversations for Bot UIDs: {bot_uids}, Load messages: {load_messages}")
        statement = select(ConversationORM).where(ConversationORM.bot_uid.in_(bot_uids))
        if load_messages:
             statement = statement.options(selectinload(ConversationORM.messages))
        # Add ordering if needed, e.g., by last updated timestamp of conversation
        # statement = statement.order_by(ConversationORM.updated_at.desc())

        try:
            result = await self._session.execute(statement)
            orm_results = result.scalars().unique().all() # Use unique() if joining might cause duplicates
            entities = [self._mapper.to_entity(orm_obj) for orm_obj in orm_results if orm_obj]
            logger.debug(f"Found {len(entities)} conversations for {len(bot_uids)} bot UIDs.")
            return entities
        except Exception as e:
            logger.error(f"Error finding conversations by bot UIDs: {e}", exc_info=True)
            return []

    async def find_by_bot_uids_and_platform(
        self,
        bot_uids: List[UUID],
        platform: ChatPlatform,
        load_messages: bool = False
        ) -> List[ConversationEntity]:
        """Finds conversations for specific bots filtered by platform."""
        if not bot_uids: return []
        platform_value = platform.value # Get string value from Enum
        logger.debug(f"Finding conversations for Bot UIDs: {bot_uids} and Platform: {platform_value}, Load messages: {load_messages}")
        statement = select(ConversationORM).where(
            ConversationORM.bot_uid.in_(bot_uids),
            ConversationORM.platform == platform_value
        )
        if load_messages:
             statement = statement.options(selectinload(ConversationORM.messages))
        # statement = statement.order_by(ConversationORM.updated_at.desc())

        try:
            result = await self._session.execute(statement)
            orm_results = result.scalars().unique().all()
            entities = [self._mapper.to_entity(orm_obj) for orm_obj in orm_results if orm_obj]
            logger.debug(f"Found {len(entities)} conversations for {len(bot_uids)} bot UIDs and platform {platform_value}.")
            return entities
        except Exception as e:
            logger.error(f"Error finding conversations by bot UIDs and platform: {e}", exc_info=True)
            return []

    async def find_single_by_bot_uid_and_platform(
        self,
        bot_uid: UUID,
        platform: ChatPlatform,
        load_messages: bool = True
        ) -> Optional[ConversationEntity]:
        """Finds a single conversation for a specific bot and platform."""
        platform_value = platform.value
        logger.debug(f"Finding single conversation for Bot UID: {bot_uid} and Platform: {platform_value}, Load messages: {load_messages}")
        statement = select(ConversationORM).where(
            ConversationORM.bot_uid == bot_uid,
            ConversationORM.platform == platform_value
        )
        if load_messages:
             statement = statement.options(selectinload(ConversationORM.messages))

        try:
            result = await self._session.execute(statement)
            # Use scalar_one_or_none as we expect zero or one result
            orm_obj = result.scalar_one_or_none()
            if not orm_obj:
                 logger.debug(f"Single conversation not found for Bot={bot_uid}, Platform='{platform_value}'")
                 return None
            return self._mapper.to_entity(orm_obj)
        except Exception as e:
            logger.error(f"Error finding single conversation (Bot={bot_uid}, Platform='{platform_value}'): {e}", exc_info=True)
            return None

    async def find_by_platform_and_sender_id(self, platform: str, sender_id: str, bot_uid: UUID) -> Optional[
        ConversationEntity]:
        """Finds a conversation by platform, sender_id and bot_uid, loading messages."""
        stmt = (
            select(ConversationORM)
            .options(selectinload(ConversationORM.messages))  # Eagerly load messages
            .where(
                ConversationORM.platform == platform,
                ConversationORM.sender_id == sender_id,  # Access sender_id via participant
                ConversationORM.bot_uid == bot_uid
            )
        )
        result = await self._session.execute(stmt)
        orm_obj = result.scalar_one_or_none()  # Use scalar_one_or_none
        return self._mapper.to_entity(orm_obj) if orm_obj else None

