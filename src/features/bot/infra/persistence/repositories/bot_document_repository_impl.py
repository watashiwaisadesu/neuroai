# src/features/bot/infra/persistence/repositories/bot_document_repository_impl.py (New file)

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from uuid import UUID
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete

from src.features.bot.domain.repositories.bot_document_repository import BotDocumentRepository
from src.features.bot.domain.entities.bot_document_entity import BotDocumentEntity
from src.features.bot.infra.persistence.models.bot_document import BotDocumentORM
from src.features.bot.infra.mappers.bot_document_mapper import BotDocumentMapper  # To be created
from src.features.bot.exceptions.bot_exceptions import DocumentNotFoundError  # Example




class BotDocumentRepositoryImpl(BotDocumentRepository):
    _session: AsyncSession
    _mapper: BotDocumentMapper

    def __init__(self, session: AsyncSession):
        self._session = session
        self._mapper = BotDocumentMapper(BotDocumentEntity, BotDocumentORM)  # Pass classes
        logger.debug("BotDocumentRepositoryImpl initialized.")

    async def create(self, entity: BotDocumentEntity) -> BotDocumentEntity:
        orm_obj = self._mapper.from_entity(entity)
        if not orm_obj:
            raise ValueError("Failed to map BotDocumentEntity to ORM for creation.")
        self._session.add(orm_obj)
        try:
            await self._session.flush()
            await self._session.refresh(orm_obj)
            return self._mapper.to_entity(orm_obj)
        except IntegrityError as e:
            logger.error(f"IntegrityError creating document for bot {entity.bot_uid}: {e}", exc_info=True)
            await self._session.rollback()
            raise  # Or a specific DocumentUploadFailedError
        except Exception as e:
            logger.error(f"Error creating document for bot {entity.bot_uid}: {e}", exc_info=True)
            await self._session.rollback()
            raise

    async def create_many(self, entities: List[BotDocumentEntity]) -> List[BotDocumentEntity]:
        if not entities:
            return []
        orm_objs = [self._mapper.from_entity(e) for e in entities if e]
        self._session.add_all(orm_objs)
        try:
            await self._session.flush()
            # Refreshing multiple objects needs care or individual refresh
            # For simplicity, we'll map back from the input entities if no DB defaults change them,
            # or re-fetch if necessary. Here, we assume from_entity -> to_entity is safe after flush.
            # A more robust way is to refresh each orm_obj and map back.
            refreshed_entities = []
            for orm_obj in orm_objs:  # Assuming flush populated UIDs if they were None
                await self._session.refresh(orm_obj)
                refreshed_entities.append(self._mapper.to_entity(orm_obj))
            return refreshed_entities
        except IntegrityError as e:
            logger.error(f"IntegrityError creating multiple documents: {e}", exc_info=True)
            await self._session.rollback()
            raise
        except Exception as e:
            logger.error(f"Error creating multiple documents: {e}", exc_info=True)
            await self._session.rollback()
            raise

    async def find_by_bot_uid(self, bot_uid: UUID) -> List[BotDocumentEntity]:
        stmt = select(BotDocumentORM).where(BotDocumentORM.bot_uid == bot_uid)
        result = await self._session.execute(stmt)
        return [self._mapper.to_entity(orm) for orm in result.scalars().all() if orm]

    async def find_by_uid(self, uid: UUID) -> Optional[BotDocumentEntity]:
        orm_obj = await self._session.get(BotDocumentORM, uid)
        return self._mapper.to_entity(orm_obj) if orm_obj else None

    async def delete_by_uid(self, uid: UUID) -> None:
        orm_obj = await self._session.get(BotDocumentORM, uid)
        if not orm_obj:
            raise DocumentNotFoundError(f"Document with UID {uid} not found for deletion.")
        await self._session.delete(orm_obj)
        await self._session.flush()

    async def find_by_uids_and_bot_uid(self, document_uids: List[UUID], bot_uid: UUID) -> List[BotDocumentEntity]:
        """Finds documents by their UIDs, ensuring they belong to the specified bot."""
        if not document_uids:
            return []
        logger.debug(f"Finding documents by UIDs {document_uids} for bot {bot_uid}")
        stmt = select(BotDocumentORM).where(
            BotDocumentORM.uid.in_(document_uids),
            BotDocumentORM.bot_uid == bot_uid
        )
        result = await self._session.execute(stmt)
        return [self._mapper.to_entity(orm) for orm in result.scalars().all() if orm]

    async def delete_by_uids(self, uids: List[UUID]) -> int:
        """Deletes multiple documents by their UIDs. Returns count of deleted documents."""
        if not uids:
            return 0
        logger.debug(f"Attempting to delete documents by UIDs: {uids}")
        statement = delete(BotDocumentORM).where(BotDocumentORM.uid.in_(uids))
        try:
            result = await self._session.execute(statement)
            await self._session.flush()  # Ensure deletes are executed
            deleted_count = result.rowcount
            logger.info(f"Successfully executed delete for {deleted_count} document(s) with UIDs: {uids}")
            return deleted_count
        except Exception as e:
            logger.error(f"Error deleting documents by UIDs {uids}: {e}", exc_info=True)
            await self._session.rollback()
