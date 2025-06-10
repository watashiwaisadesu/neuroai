from uuid import UUID
from typing import List, Optional
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from src.features.bot.domain.entities.bot_entity import BotEntity
from src.features.bot.domain.repositories.bot_repository import BotRepository
from src.features.bot.infra.persistence.models.bot import BotORM
from src.features.bot.infra.mappers.bot_mapper import BotMapper
from src.features.bot.exceptions.bot_exceptions import (
    BotNotFoundError,
    BotAlreadyExistsError,
)




class BotRepositoryImpl(BotRepository):
    def __init__(self, session: AsyncSession):
        self._session = session
        self._mapper = BotMapper()

    async def create(self, entity: BotEntity) -> BotEntity:
        orm_obj = self._mapper.from_entity(entity)
        self._session.add(orm_obj)

        try:
            await self._session.flush()  # May raise IntegrityError
            await self._session.refresh(orm_obj)
            return self._mapper.to_entity(orm_obj)
        except IntegrityError as e:
            logger.error(f"❌ IntegrityError while creating bot: {e}")
            await self._session.rollback()
            raise BotAlreadyExistsError()

    async def update(self, entity: BotEntity) -> BotEntity:
        """
        Updates an existing Bot record in the database based on the provided BotEntity.
        """
        # 1. Fetch the existing ORM object
        existing_orm = await self._session.get(BotORM, entity.uid)
        if not existing_orm:
            logger.warning(f"Bot with UID {entity.uid} not found for update.")
            raise BotNotFoundError(f"Bot with UID {entity.uid} not found.")

        # 2. Update existing ORM directly from the entity
        # Handle direct attributes. Note: _user_uid and _bot_type are internal.
        # The properties entity.user_uid and entity.bot_type give access to their values.
        # The ORM should map to 'user_uid' and 'bot_type' directly, not '_user_uid'.
        # Ensure your BotORM defines `user_uid` and `bot_type` fields.
        existing_orm.user_uid = entity.user_uid  # Use the public property
        existing_orm.name = entity.name
        existing_orm.status = entity.status
        existing_orm.tariff = entity.tariff
        existing_orm.auto_deduction = entity.auto_deduction
        existing_orm.crm_lead_id = entity.crm_lead_id
        existing_orm.bot_type = entity.bot_type  # Use the public property

        # CRITICAL FIX: Handle potentially None value objects or their attributes
        # The ORM might have NOT NULL constraints, so convert None to default values
        # if the DTOs do not allow None.
        # Always ensure you're mapping to the ORM's field names (e.g., `instructions`, not `_instructions`).
        ai_settings = entity.ai_settings
        if ai_settings:
            existing_orm.instructions = ai_settings.instructions if ai_settings.instructions is not None else ""
            existing_orm.temperature = ai_settings.temperature if ai_settings.temperature is not None else 0.0
            existing_orm.top_p = ai_settings.top_p if ai_settings.top_p is not None else 0.0
            existing_orm.top_k = ai_settings.top_k if ai_settings.top_k is not None else 0
            existing_orm.max_response = ai_settings.max_response if ai_settings.max_response is not None else 0
            existing_orm.repetition_penalty = ai_settings.repetition_penalty if ai_settings.repetition_penalty is not None else 0.0
            existing_orm.generation_model = ai_settings.generation_model if ai_settings.generation_model is not None else ""
        else:
            # If ai_settings itself is None, ensure ORM fields are set to defaults
            existing_orm.instructions = ""
            existing_orm.temperature = 0.0
            existing_orm.top_p = 0.0
            existing_orm.top_k = 0
            existing_orm.max_response = 0
            existing_orm.repetition_penalty = 0.0
            existing_orm.generation_model = ""

        quota = entity.quota
        if quota:
            existing_orm.token_limit = quota.token_limit if quota.token_limit is not None else 0
            existing_orm.tokens_left = quota.tokens_left if quota.tokens_left is not None else 0
        else:
            # If quota itself is None, ensure ORM fields are set to defaults
            existing_orm.token_limit = 0
            existing_orm.tokens_left = 0

        # Handle timestamp update (usually handled by DB triggers or SQLAlchemy's default_factory/onupdate)
        # If your ORM model has server_default or onupdate=func.now(), you don't need to set it here.
        # If not, and you want to manage it from the application, you can:
        # existing_orm.updated_at = datetime.now(timezone.utc) # Use timezone-aware datetime

        try:
            # The session should already be in a transaction via UoW.__aenter__
            # No need for self._session.begin() here.
            await self._session.flush()  # Push changes to DB
            await self._session.refresh(existing_orm)  # Refresh to get latest DB values (e.g., updated_at)

            # Map the updated ORM object back to an entity and return it
            return self._mapper.to_entity(existing_orm)
        except IntegrityError as e:
            logger.error(f"IntegrityError during Bot update (UID: {entity.uid}): {e}")
            # The UoW's __aexit__ will handle rollback if an exception propagates
            raise  # Re-raise to let the UoW handle the rollback
        except Exception as e:
            logger.error(f"Error during Bot update (UID: {entity.uid}): {e}", exc_info=True)
            # The UoW's __aexit__ will handle rollback if an exception propagates
            raise  # Re-raise to let the UoW handle the rollback


    async def delete_by_uid(self, uid: UUID) -> None:
        bot = await self._session.get(BotORM, uid)
        if not bot:
            raise BotNotFoundError()
        await self._session.delete(bot)
        await self._session.flush()  # Just flush

    async def find_by_uid(self, uid: UUID) -> Optional[BotEntity]:
        bot = await self._session.get(BotORM, uid)
        return self._mapper.to_entity(bot) if bot else None

    async def find_by_uids(self, uids: List[UUID]) -> List[BotEntity]:
        """Finds multiple bots by their UIDs using an IN clause."""
        if not uids:
            logger.debug("find_by_uids received empty list, returning empty list.")
            return []  # Return empty list if no UIDs provided

        # Ensure UIDs are unique if necessary, although IN clause handles duplicates
        unique_uids = list(set(uids))
        logger.debug(f"Finding bots by UIDs: {unique_uids}")
        statement = select(BotORM).where(BotORM.uid.in_(unique_uids))
        try:
            result = await self._session.execute(statement)
            orm_results = result.scalars().all()
            # Map results, ensuring mapper handles potential None from DB if needed
            entities = [self._mapper.to_entity(orm_obj) for orm_obj in orm_results if orm_obj]
            logger.debug(f"Found {len(entities)} bots for {len(unique_uids)} requested UIDs.")
            # Optional: Check if len(entities) matches len(unique_uids) if all must exist
            return entities
        except Exception as e:
            logger.error(f"Error finding bots by UIDs: {e}", exc_info=True)
            return []  # Return empty list on error or re-raise

    async def findall(self, entity: BotEntity) -> List[BotEntity]:
        stmt = select(BotORM).where(BotORM.user_uid == entity.user_uid)
        result = await self._session.execute(stmt)
        return [self._mapper.to_entity(row) for row in result.scalars().all()]

    async def findall_by_user_uid(self, user_uid: UUID) -> List[BotEntity]:
        stmt = select(BotORM).where(BotORM.user_uid == user_uid)
        result = await self._session.execute(stmt)
        return [self._mapper.to_entity(row) for row in result.scalars().all()]
