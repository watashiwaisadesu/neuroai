# src/features/bot/infra/persistence/repositories/bot_service_repository_impl.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import List, Optional  # Import Type
from uuid import UUID

from sqlalchemy import delete  # Import delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.features.bot.domain.entities.bot_service_entity import BotServiceEntity
from src.features.bot.domain.repositories.bot_service_repository import BotServiceRepository
from src.features.bot.exceptions.bot_exceptions import ServiceNotFoundError, \
    ServiceAlreadyLinkedError
from src.features.bot.infra.mappers.bot_service_mapper import BotServiceMapper
from src.features.bot.infra.persistence.models.bot_service import BotServiceORM



class BotServiceRepositoryImpl(BotServiceRepository):
    """Concrete implementation of the BotServiceRepository using SQLAlchemy."""

    _session: AsyncSession
    _mapper: BotServiceMapper

    def __init__(self, session: AsyncSession):
        self._session = session
        # Instantiate the specific mapper
        # Ensure BotServiceEntity/ORM are correctly imported/defined
        self._mapper = BotServiceMapper(BotServiceEntity, BotServiceORM) # Pass classes if needed
        logger.debug("BotServiceRepositoryImpl initialized.")

    # --- Implementations from BaseRepository ---

    async def create(self, entity: BotServiceEntity) -> BotServiceEntity:
        """Creates a new BotService record."""
        orm_obj = self._mapper.from_entity(entity)
        if not orm_obj:
             raise ValueError("Failed to map BotServiceEntity to ORM object.")

        logger.debug(f"Adding BotService ORM object to session: Bot={entity.bot_uid}, Platform={entity.platform}")
        self._session.add(orm_obj)
        try:
            await self._session.flush()
            # Refresh to get DB defaults like created_at/updated_at if BaseEntity handles them
            await self._session.refresh(orm_obj)
            logger.info(f"Successfully flushed creation for BotService: Bot={entity.bot_uid}, Platform={entity.platform}, UID={orm_obj.uid}")
            # Map back the refreshed state
            return self._mapper.to_entity(orm_obj)
        except IntegrityError as e:
            logger.error(f"IntegrityError creating BotService (Bot={entity.bot_uid}, Platform={entity.platform}): {e}", exc_info=True)
            await self._session.rollback()
            # Could be duplicate primary key (uid) or unique constraint (bot_uid, platform)
            # Or foreign key violation
            raise ServiceAlreadyLinkedError(f"Service '{entity.platform}' might already be linked or related data is invalid.") from e
        except Exception as e:
            logger.error(f"Error during BotService creation flush (Bot={entity.bot_uid}, Platform={entity.platform}): {e}", exc_info=True)
            await self._session.rollback()
            raise

    async def update(self, entity: BotServiceEntity) -> BotServiceEntity:
        """Updates an existing service link (e.g., its status or linked_account_uid)."""  # Updated docstring
        logger.debug(f"Attempting to update BotService with UID: {entity.uid}")
        existing_orm = await self._session.get(BotServiceORM, entity.uid)
        if not existing_orm:
            logger.warning(f"BotService not found for update with UID: {entity.uid}")
            raise ServiceNotFoundError(f"Service link with UID {entity.uid} not found.")

        # Ensure immutable fields aren't changed (Good practice!)
        if existing_orm.bot_uid != entity.bot_uid or existing_orm.platform != entity.platform:
            logger.error(
                f"Attempted to change immutable identifiers (bot_uid/platform) during update for service UID {entity.uid}")
            raise ValueError("Cannot change bot_uid or platform during service link update.")

        updated = False  # Flag to track if any actual changes were made

        # --- Update mutable attributes ---
        # 1. Update status
        if hasattr(entity, 'status') and existing_orm.status != entity.status:
            logger.debug(
                f"Updating status from '{existing_orm.status}' to '{entity.status}' for service UID {entity.uid}")
            existing_orm.status = entity.status
            updated = True

        # 2. Update linked_account_uid (This was missing from your explicit update logic)
        #    Your BotPlatformLinkerService sets entity.linked_account_uid before calling this update method.
        #    This block ensures that change is applied to the ORM object.
        if hasattr(entity, 'linked_account_uid'):
            # Check if the attribute exists and if its value is different or if the existing ORM value was None and now it's set.
            # A simple inequality check handles cases where one is None and the other is not.
            if existing_orm.linked_account_uid != entity.linked_account_uid:
                logger.debug(
                    f"Updating linked_account_uid from '{existing_orm.linked_account_uid}' to '{entity.linked_account_uid}' "
                    f"for service UID {entity.uid}"
                )
                existing_orm.linked_account_uid = entity.linked_account_uid
                updated = True

        if hasattr(entity, 'service_details'):
            # For JSON fields, direct comparison should work if the objects are consistently structured (e.g., dicts).
            # If entity.service_details is None and existing_orm.service_details is {}, they are different.
            if existing_orm.service_details != entity.service_details:
                logger.debug(
                    f"Updating service_details for service UID {entity.uid}"
                    # f"from '{existing_orm.service_details}' to '{entity.service_details}'" # Logging full dicts can be verbose
                )
                existing_orm.service_details = entity.service_details  # Apply the change to the ORM object
                updated = True

        # Add other updatable fields if necessary following the same pattern

        if not updated:
            logger.debug(f"No changes detected for service UID {entity.uid}. Returning current state.")
            # Return the entity mapped from the existing_orm to reflect the true persisted state.
            return self._mapper.to_entity(existing_orm)

        try:
            # The changes to existing_orm (which is tracked by the session) will be flushed.
            await self._session.flush()
            await self._session.refresh(existing_orm)  # Refresh to get DB triggers/defaults and confirm state
            logger.info(f"Successfully flushed update for service UID {entity.uid}")
            return self._mapper.to_entity(existing_orm)  # Map the refreshed ORM object back to an entity
        except Exception as e:
            logger.error(f"Error during service link update (UID: {entity.uid}): {e}", exc_info=True)
            # Rollback should ideally be handled by the Unit of Work context manager
            # that wraps the service call which uses this repository method.
            # If self._session is part of that UoW, an explicit rollback here might be okay
            # or could conflict. It's safer if UoW handles it.
            # await self._session.rollback() # Consider if UoW handles this.
            raise

    async def delete_by_uid(self, uid: UUID) -> None:
        """Deletes a service link entry by its own unique identifier."""
        logger.debug(f"Attempting to delete service link by UID: {uid}")
        orm_obj = await self._session.get(BotServiceORM, uid)
        if not orm_obj:
            logger.warning(f"Service link not found for deletion by UID: {uid}")
            raise ServiceNotFoundError(f"Service link with UID {uid} not found.")
        try:
            await self._session.delete(orm_obj)
            await self._session.flush()
            logger.info(f"Successfully deleted service link with UID: {uid}")
        except Exception as e:
            logger.error(f"Error deleting service link by UID {uid}: {e}", exc_info=True)
            await self._session.rollback()
            raise

    async def find_by_uid(self, uid: UUID) -> Optional[BotServiceEntity]:
        """Finds a service link entry by its own unique identifier."""
        logger.debug(f"Finding service link by UID: {uid}")
        orm_obj = await self._session.get(BotServiceORM, uid)
        if not orm_obj:
             logger.debug(f"Service link not found by UID: {uid}")
             return None
        try:
            return self._mapper.to_entity(orm_obj)
        except Exception as e:
            logger.error(f"Error mapping service link found by UID {uid}: {e}", exc_info=True)
            return None

    # --- Implementations for specific methods ---

    async def find_by_bot_uid(self, bot_uid: UUID) -> List[BotServiceEntity]:
        """Finds all services associated with a specific bot."""
        logger.debug(f"Finding all services for Bot={bot_uid}")
        statement = select(BotServiceORM).where(BotServiceORM.bot_uid == bot_uid)
        try:
            result = await self._session.execute(statement)
            orm_results = result.scalars().all()
            entities = [self._mapper.to_entity(orm_obj) for orm_obj in orm_results if orm_obj]
            logger.debug(f"Found {len(entities)} services for Bot={bot_uid}")
            return entities
        except Exception as e:
            logger.error(f"Error finding services for Bot={bot_uid}: {e}", exc_info=True)
            return []

    async def find_by_bot_and_platform(self, bot_uid: UUID, platform: str) -> Optional[BotServiceEntity]:
        """Finds a specific service link by bot and platform name."""
        logger.debug(f"Finding service link for Bot={bot_uid}, Platform='{platform}'")
        statement = select(BotServiceORM).where(
            BotServiceORM.bot_uid == bot_uid,
            BotServiceORM.platform == platform
        )
        try:
            result = await self._session.execute(statement)
            orm_obj = result.scalar_one_or_none()
            if not orm_obj:
                 logger.debug(f"Service link not found for Bot={bot_uid}, Platform='{platform}'")
                 return None
            return self._mapper.to_entity(orm_obj)
        except Exception as e:
            logger.error(f"Error finding service link (Bot={bot_uid}, Platform='{platform}'): {e}", exc_info=True)
            return None

    async def delete_by_bot_and_platform(self, bot_uid: UUID, platform: str) -> bool:
        """Deletes a service link by bot and platform name. Returns True if deleted."""
        logger.debug(f"Attempting to delete service link Bot={bot_uid}, Platform='{platform}'")
        statement = delete(BotServiceORM).where(
             BotServiceORM.bot_uid == bot_uid,
             BotServiceORM.platform == platform
        )
        try:
            result = await self._session.execute(statement)
            await self._session.flush() # Ensure delete is executed
            deleted_count = result.rowcount
            if deleted_count > 0:
                 logger.info(f"Successfully deleted service link Bot={bot_uid}, Platform='{platform}'")
                 return True
            else:
                 logger.warning(f"Service link not found for deletion: Bot={bot_uid}, Platform='{platform}'")
                 return False # Indicate link wasn't found
        except Exception as e:
            logger.error(f"Error deleting service link (Bot={bot_uid}, Platform='{platform}'): {e}", exc_info=True)
            await self._session.rollback()
            raise

    async def find_first_by_bot_platform_status(
            self,
            bot_uid: UUID,
            platform: str,
            status: str,
    ) -> Optional[BotServiceEntity]:
        """
        Finds the first BotServiceEntity that matches the given bot_uid,
        platform name, and status.
        """
        stmt = (
            select(BotServiceORM)
            .where(
                BotServiceORM.bot_uid == bot_uid,
                BotServiceORM.platform == platform,
                BotServiceORM.status == status
            )
            # If "first" implies a specific order (e.g., oldest), add order_by:
            # .order_by(BotServiceModelDb.created_at.asc()) # Assuming a 'created_at' field
            .limit(1)  # Important to ensure only one record is processed if multiple match
        )

        result = await self._session.execute(stmt)
        orm_obj = result.scalar_one_or_none()  # Fetches the first record or None

        return self._mapper.to_entity(orm_obj)



