# src/features/integrations/telegram/infra/persistence/repositories/telegram_account_link_repository_impl.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from uuid import UUID
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy import delete # Import delete

# Import domain interface and entity
from src.features.integrations.messengers.telegram.domain.repositories.telegram_account_link_repository import TelegramAccountLinkRepository
from src.features.integrations.messengers.telegram.domain.entities.telegram_account_link_entity import TelegramAccountLinkEntity

# Import infrastructure components
from src.features.integrations.messengers.telegram.infra.persistence.models.telegram_account_link import TelegramAccountLinkORM
from src.features.integrations.messengers.telegram.infra.mappers.telegram_account_link_mapper import TelegramAccountLinkMapper

# Import custom exceptions if needed
from src.features.integrations.messengers.telegram.exceptions.telegram_exceptions import TelegramLinkNotFoundError, TelegramLinkAlreadyExistsError # Define these



class SQLAlchemyTelegramAccountLinkRepository(TelegramAccountLinkRepository):
    """Concrete implementation of ITelegramAccountLinkRepository using SQLAlchemy."""

    _session: AsyncSession
    _mapper: TelegramAccountLinkMapper

    def __init__(self, session: AsyncSession):
        self._session = session
        self._mapper = TelegramAccountLinkMapper(TelegramAccountLinkEntity, TelegramAccountLinkORM)
        logger.debug("TelegramAccountLinkRepositoryImpl initialized.")

    async def create(self, entity: TelegramAccountLinkEntity) -> TelegramAccountLinkEntity:
        orm_obj = self._mapper.from_entity(entity)
        if not orm_obj:
             raise ValueError("Failed to map TelegramAccountLinkEntity to ORM for creation.")
        self._session.add(orm_obj)
        try:
            await self._session.flush()
            await self._session.refresh(orm_obj) # Get DB defaults
            logger.info(f"Created TelegramAccountLink for bot {entity.bot_uid}, phone {entity.phone_number}")
            return self._mapper.to_entity(orm_obj)
        except IntegrityError as e:
            logger.error(f"IntegrityError creating TelegramAccountLink: {e}", exc_info=True)
            await self._session.rollback()
            raise TelegramLinkAlreadyExistsError(f"Link for phone {entity.phone_number} or TG ID {entity.telegram_user_id} might already exist.") from e
        except Exception as e:
            logger.error(f"Error creating TelegramAccountLink: {e}", exc_info=True)
            await self._session.rollback()
            raise

    async def update(self, entity: TelegramAccountLinkEntity) -> TelegramAccountLinkEntity:
        orm_obj = await self._session.get(TelegramAccountLinkORM, entity.uid)
        if not orm_obj:
            raise TelegramLinkNotFoundError(f"TelegramAccountLink with UID {entity.uid} not found for update.")

        # Update mutable fields from entity to orm_obj
        orm_obj.bot_uid = entity.bot_uid
        orm_obj.telegram_user_id = entity.telegram_user_id
        orm_obj.phone_number = entity.phone_number # Should phone be updatable?
        orm_obj.username = entity.username
        orm_obj.session_string = entity.session_string
        orm_obj.phone_code_hash = entity.phone_code_hash
        orm_obj.is_active = entity.is_active
        orm_obj.last_connected_at = entity.last_connected_at
        # bot_uid and platform_user_uid are usually not changed after creation
        # Timestamps (updated_at) handled by SQLAlchemyBase/mixin

        try:
            await self._session.flush()
            await self._session.refresh(orm_obj)
            logger.info(f"Updated TelegramAccountLink UID: {entity.uid}")
            return self._mapper.to_entity(orm_obj)
        except Exception as e:
            logger.error(f"Error updating TelegramAccountLink UID {entity.uid}: {e}", exc_info=True)
            await self._session.rollback()
            raise

    async def delete_by_uid(self, uid: UUID) -> None:
        orm_obj = await self._session.get(TelegramAccountLinkORM, uid)
        if not orm_obj:
            raise TelegramLinkNotFoundError(f"TelegramAccountLink with UID {uid} not found for deletion.")
        try:
            await self._session.delete(orm_obj)
            await self._session.flush()
            logger.info(f"Deleted TelegramAccountLink UID: {uid}")
        except Exception as e:
            logger.error(f"Error deleting TelegramAccountLink UID {uid}: {e}", exc_info=True)
            await self._session.rollback()
            raise

    async def find_by_uid(self, uid: UUID) -> Optional[TelegramAccountLinkEntity]:
        orm_obj = await self._session.get(TelegramAccountLinkORM, uid)
        return self._mapper.to_entity(orm_obj) if orm_obj else None

    async def find_by_phone_number(self, phone_number: str) -> Optional[TelegramAccountLinkEntity]:
        stmt = select(TelegramAccountLinkORM).where(TelegramAccountLinkORM.phone_number == phone_number)
        result = await self._session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        return self._mapper.to_entity(orm_obj) if orm_obj else None

    async def find_by_telegram_user_id(self, telegram_user_id: str) -> Optional[TelegramAccountLinkEntity]:
        stmt = select(TelegramAccountLinkORM).where(TelegramAccountLinkORM.telegram_user_id == telegram_user_id)
        result = await self._session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        return self._mapper.to_entity(orm_obj) if orm_obj else None

    async def find_by_bot_uid(self, bot_uid: UUID) -> Optional[TelegramAccountLinkEntity]:
        # Assuming one active link per bot. If multiple, this should return List.
        stmt = select(TelegramAccountLinkORM).where(
            TelegramAccountLinkORM.bot_uid == bot_uid,
            TelegramAccountLinkORM.is_active == True # Often want the active one
        )
        result = await self._session.execute(stmt)
        orm_obj = result.scalar_one_or_none() # Or .first() if multiple active possible but you want one
        return self._mapper.to_entity(orm_obj) if orm_obj else None

    async def find_all_active_sessions(self) -> List[TelegramAccountLinkEntity]:
        stmt = select(TelegramAccountLinkORM).where(TelegramAccountLinkORM.is_active == True, TelegramAccountLinkORM.session_string.isnot(None))
        result = await self._session.execute(stmt)
        return [self._mapper.to_entity(orm) for orm in result.scalars().all() if orm]

