# src/features/support/infra/persistence/repositories/sqlalchemy_support_repository.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError, NoResultFound

from src.features.support.domain.entities.support_entity import SupportEntity # Renamed import
from src.features.support.domain.repossitories.support_repository import SupportRepository
from src.features.support.domain.value_objects.support_enums import SupportCategory
from src.features.support.infra.mappers.support_mapper import SupportMapper # Renamed import

from src.features.support.infra.persistence.models.support_orm import SupportORM # Renamed import
from src.features.support.exceptions.support_exceptions import SupportNotFoundError, SupportAlreadyExistsError




class SQLAlchemySupportRepository(SupportRepository):
    def __init__(self, session: AsyncSession):
        self._session = session
        self._mapper = SupportMapper() # Renamed mapper

    async def create(self, entity: SupportEntity) -> SupportEntity: # Renamed create to add
        orm_obj = self._mapper.from_entity(entity)
        self._session.add(orm_obj)
        try:
            await self._session.flush() # Flush to assign PK/defaults and handle relationships
            await self._session.refresh(orm_obj) # Get fresh state from DB, including relationship IDs
            logger.info(f"Support item {orm_obj.uid} created in DB.") # Updated log message
            return self._mapper.to_entity(orm_obj)
        except IntegrityError as e:
            logger.error(f"IntegrityError creating support item: {e}", exc_info=True) # Updated log message
            raise SupportAlreadyExistsError("Support item with this UID already exists or other integrity violation.") from e # Updated message
        except Exception as e:
            logger.error(f"Error creating support item: {e}", exc_info=True) # Updated log message
            raise

    async def get_by_uid(self, uid: UUID) -> Optional[SupportEntity]:
        # Using selectinload to eagerly load attachments with the main support item
        query = select(SupportORM).where(SupportORM.uid == uid).options(
            joinedload(SupportORM.attachments) # Eager load attachments if relationship exists
        )
        result = await self._session.execute(query)
        # Apply .unique() for single object retrieval if eager loading a collection
        orm_obj = result.scalars().unique().first()
        if orm_obj:
            return self._mapper.to_entity(orm_obj)
        return None

    async def update(self, entity: SupportEntity) -> SupportEntity:
        # Fetch with selectinload to ensure attachments are loaded for modification
        stmt = select(SupportORM).where(SupportORM.uid == entity.uid) #.options(selectinload(SupportORM.attachments))
        result = await self._session.execute(stmt)
        existing_orm = result.scalar_one_or_none()

        if not existing_orm:
            logger.warning(f"Support item {entity.uid} not found for update.") # Updated log message
            raise SupportNotFoundError(f"Support item with UID {entity.uid} not found.") # Updated message

        # Update ORM attributes from entity
        existing_orm.user_uid = entity.user_uid
        existing_orm.email = entity.email
        existing_orm.message = entity.message
        existing_orm.subject = entity.subject

        # Handle attachments: clear existing and add new ones from entity
        # This leverages SQLAlchemy's cascade and delete-orphan
        existing_orm.attachments.clear()
        for att_entity in entity.attachments:
            # Assuming your mapper or direct construction creates AttachmentORM from AttachmentEntity
            existing_orm.attachments.append(
                self._mapper.from_entity(att_entity))  # You need a to_attachment_orm method in your mapper

        await self._session.flush()
        existing_orm.status = entity.status.value
        existing_orm.priority = entity.priority.value
        existing_orm.category = entity.category.value if entity.category else None
        existing_orm.updated_at = entity.updated_at


        try:
            await self._session.flush()
            await self._session.refresh(existing_orm) # Refresh to get latest state of attachments
            logger.info(f"Support item {entity.uid} updated in DB.") # Updated log message
            return self._mapper.to_entity(existing_orm)
        except IntegrityError as e:
            logger.error(f"IntegrityError updating support item {entity.uid}: {e}", exc_info=True) # Updated log message
            raise
        except Exception as e:
            logger.error(f"Error updating support item {entity.uid}: {e}", exc_info=True) # Updated log message
            raise

    async def delete_by_uid(self, uid: UUID) -> None:
        stmt = select(SupportORM).where(SupportORM.uid == uid)
        result = await self._session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        if not orm_obj:
            logger.warning(f"Support item {uid} not found for deletion.") # Updated log message
            raise SupportNotFoundError(f"Support item with UID {uid} not found for deletion.") # Updated message
        await self._session.delete(orm_obj)
        logger.info(f"Support item {uid} deleted from DB.") # Updated log message

    async def get_all_by_user_uid(self, user_uid: UUID, category: Optional[SupportCategory] = None) -> List[
        SupportEntity]:
        """
        Retrieves all support requests for a given user, optionally filtered by category.
        Includes eager loading of attachments to prevent N+1 queries.
        """
        query = select(SupportORM).where(SupportORM.user_uid == user_uid).options(
            # CRITICAL: This is the `joinedload` that causes the issue if not handled with .unique()
            joinedload(SupportORM.attachments)
        )

        if category:
            query = query.where(SupportORM.category == category)

        result = await self._session.execute(query)

        # *** THE CRITICAL FIX IS HERE ***
        # Call .unique() on the result.scalars() before .all() to deduplicate parent objects
        orm_objects = result.scalars().unique().all()  # Changed from .all() to .unique().all()

        return [self._mapper.to_entity(orm_obj) for orm_obj in orm_objects]

    async def get_all(self) -> List[SupportEntity]:
        stmt = select(SupportORM).order_by(SupportORM.created_at.desc()) #.options(selectinload(SupportORM.attachments))
        result = await self._session.execute(stmt)
        return [self._mapper.to_entity(orm_obj) for orm_obj in result.scalars().all()]

