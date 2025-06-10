# src/features/bot/infra/persistence/repositories/bot_participant_repository_impl.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from uuid import UUID
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy import delete

# Import domain interfaces and entities
from src.features.bot.domain.repositories.bot_participant_repository import BotParticipantRepository
from src.features.bot.domain.entities.bot_participant_entity import BotParticipantEntity

# Import infrastructure components
from src.features.bot.infra.persistence.models.bot_participant import BotParticipantORM
from src.features.bot.infra.mappers.bot_participant_mapper import BotParticipantMapper


from src.features.bot.exceptions.bot_exceptions import ParticipantNotFoundError, ParticipantAlreadyExistsError




class BotParticipantRepositoryImpl(BotParticipantRepository):
    """Concrete implementation of the BotParticipantRepository using SQLAlchemy."""

    _session: AsyncSession
    _mapper: BotParticipantMapper

    def __init__(self, session: AsyncSession):
        self._session = session
        # Instantiate the specific mapper
        # Ensure BotParticipantEntity/ORM are correctly imported/defined
        self._mapper = BotParticipantMapper(BotParticipantEntity, BotParticipantORM)
        logger.debug("BotParticipantRepositoryImpl initialized.")

    async def create(self, entity: BotParticipantEntity) -> BotParticipantEntity:
        """Creates a new BotParticipant record."""
        orm_obj = self._mapper.from_entity(entity)
        if not orm_obj:
             raise ValueError("Failed to map BotParticipantEntity to ORM object.")

        logger.debug(f"Adding BotParticipant ORM object to session: Bot={entity.bot_uid}, User={entity.user_uid}")
        self._session.add(orm_obj)
        try:
            await self._session.flush()
            logger.info(f"Successfully flushed creation for BotParticipant: Bot={entity.bot_uid}, User={entity.user_uid}")
            return entity # Return original entity
        except IntegrityError as e:
            logger.error(f"IntegrityError creating BotParticipant (Bot={entity.bot_uid}, User={entity.user_uid}): {e}", exc_info=True)
            await self._session.rollback()
            raise ParticipantAlreadyExistsError() from e
        except Exception as e:
            logger.error(f"Error during BotParticipant creation flush (Bot={entity.bot_uid}, User={entity.user_uid}): {e}", exc_info=True)
            await self._session.rollback()
            raise

    async def find_by_bot_and_user(self, bot_uid: UUID, user_uid: UUID) -> Optional[BotParticipantEntity]:
        """Finds a specific participant entry by bot and user UID."""
        logger.debug(f"Finding participant for Bot={bot_uid}, User={user_uid}")
        statement = select(BotParticipantORM).where(
            BotParticipantORM.bot_uid == bot_uid,
            BotParticipantORM.user_uid == user_uid
        )
        try:
            result = await self._session.execute(statement)
            orm_obj = result.scalar_one_or_none()
            if not orm_obj:
                 logger.debug(f"Participant not found for Bot={bot_uid}, User={user_uid}")
                 return None
            return self._mapper.to_entity(orm_obj)
        except Exception as e:
            logger.error(f"Error finding participant (Bot={bot_uid}, User={user_uid}): {e}", exc_info=True)
            return None

    async def find_participant_role(self, bot_uid: UUID, user_uid: UUID) -> Optional[str]:
        """Finds the role of a specific participant."""
        logger.debug(f"Finding participant role for Bot={bot_uid}, User={user_uid}")
        statement = select(BotParticipantORM.role).where(
            BotParticipantORM.bot_uid == bot_uid,
            BotParticipantORM.user_uid == user_uid
        )
        try:
            result = await self._session.execute(statement)
            role = result.scalar_one_or_none()
            logger.debug(f"Found role '{role}' for participant Bot={bot_uid}, User={user_uid}")
            return role
        except Exception as e:
            logger.error(f"Error finding participant role (Bot={bot_uid}, User={user_uid}): {e}", exc_info=True)
            return None


    async def find_by_bot_uid(self, bot_uid: UUID) -> List[BotParticipantEntity]:
        """Finds all participants for a given bot UID."""
        logger.debug(f"Finding all participants for Bot={bot_uid}")
        statement = select(BotParticipantORM).where(BotParticipantORM.bot_uid == bot_uid)
        try:
            result = await self._session.execute(statement)
            orm_results = result.scalars().all()
            # Ensure mapper handles None correctly if list can contain Nones, or filter Nones
            entities = [self._mapper.to_entity(orm_obj) for orm_obj in orm_results if orm_obj]
            logger.debug(f"Found {len(entities)} participants for Bot={bot_uid}")
            return entities
        except Exception as e:
            logger.error(f"Error finding participants for Bot={bot_uid}: {e}", exc_info=True)
            return []

    # *** ADDED MISSING METHOD IMPLEMENTATION ***
    async def find_bots_by_user_uid(self, user_uid: UUID) -> List[BotParticipantEntity]:
        """Finds all participant entries for a specific user."""
        logger.debug(f"Finding all participations for User={user_uid}")
        statement = select(BotParticipantORM).where(BotParticipantORM.user_uid == user_uid)
        try:
            result = await self._session.execute(statement)
            orm_results = result.scalars().all()
            # Ensure mapper handles None correctly if list can contain Nones, or filter Nones
            entities = [self._mapper.to_entity(orm_obj) for orm_obj in orm_results if orm_obj]
            logger.debug(f"Found {len(entities)} participations for User={user_uid}")
            return entities
        except Exception as e:
            logger.error(f"Error finding participations for User={user_uid}: {e}", exc_info=True)
            return [] # Return empty list on error or re-raise

    async def delete_by_uid(self, bot_uid: UUID, user_uid: UUID) -> bool:
        """Deletes a specific participant entry by composite key."""
        # This method might be redundant if delete_by_uid exists and is preferred,
        # but implemented here based on the interface.
        logger.debug(f"Attempting to delete participant Bot={bot_uid}, User={user_uid}")
        # Find the entity first to ensure it exists and potentially get its UID for delete_by_uid
        # Or use a delete statement directly
        statement = delete(BotParticipantORM).where(
             BotParticipantORM.bot_uid == bot_uid,
             BotParticipantORM.user_uid == user_uid
        )
        try:
            result = await self._session.execute(statement)
            await self._session.flush() # Ensure delete is executed
            deleted_count = result.rowcount
            if deleted_count > 0:
                 logger.info(f"Successfully deleted participant Bot={bot_uid}, User={user_uid}")
                 return True
            else:
                 logger.warning(f"Participant not found for deletion: Bot={bot_uid}, User={user_uid}")
                 return False # Indicate participant wasn't found
        except Exception as e:
            logger.error(f"Error deleting participant (Bot={bot_uid}, User={user_uid}): {e}", exc_info=True)
            await self._session.rollback()
            raise

    async def update(self, entity: BotParticipantEntity) -> BotParticipantEntity:
        """Updates an existing participant (e.g., their role)."""
        logger.debug(f"Attempting to update participant Bot={entity.bot_uid}, User={entity.user_uid}")
        # Load existing ORM object using its primary key (assuming it's entity.uid)
        existing_orm = await self._session.get(BotParticipantORM, entity.uid)
        if not existing_orm:
            # If not found by UID, maybe try composite key? Depends on PK strategy.
            # Let's assume find by UID is the primary way.
            logger.warning(f"Participant not found for update: UID={entity.uid}")
            raise ParticipantNotFoundError(f"Participant with UID {entity.uid} not found.")

        # Ensure bot_uid and user_uid aren't being changed if they form part of identity
        if existing_orm.bot_uid != entity.bot_uid or existing_orm.user_uid != entity.user_uid:
             logger.error(f"Attempted to change immutable identifiers (bot_uid/user_uid) during update for participant UID {entity.uid}")
             # This indicates a logic error - shouldn't happen if loading by UID
             raise ValueError("Cannot change bot_uid or user_uid during participant update.")

        # Update attributes from the entity
        updated = False
        if hasattr(entity, 'role') and existing_orm.role != entity.role:
             logger.debug(f"Updating role to '{entity.role}' for participant UID {entity.uid}")
             existing_orm.role = entity.role
             updated = True
        # Add other updatable fields if necessary

        if not updated:
             logger.debug(f"No changes detected for participant UID {entity.uid}, skipping flush.")
             return entity # Return original entity if no changes

        try:
            await self._session.flush()
            await self._session.refresh(existing_orm) # Refresh to get final state
            logger.info(f"Successfully flushed update for participant UID {entity.uid}")
            # Map back the updated state
            return self._mapper.to_entity(existing_orm)
        except Exception as e:
            logger.error(f"Error during participant update (UID: {entity.uid}): {e}", exc_info=True)
            await self._session.rollback()
            raise

    async def find_by_uid(self, uid: UUID) -> Optional[BotParticipantEntity]:
        """Finds a participant entry by its own unique identifier."""
        logger.debug(f"Finding participant by UID: {uid}")
        orm_obj = await self._session.get(BotParticipantORM, uid)
        if not orm_obj:
             logger.debug(f"Participant not found by UID: {uid}")
             return None
        try:
            return self._mapper.to_entity(orm_obj)
        except Exception as e:
            logger.error(f"Error mapping participant found by UID {uid}: {e}", exc_info=True)
            return None

    async def is_participant(self, bot_uid: UUID, user_uid: UUID) -> bool:
        role = await self.find_participant_role(bot_uid, user_uid)
        return role is not None


