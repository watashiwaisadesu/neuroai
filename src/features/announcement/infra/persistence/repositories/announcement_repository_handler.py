# src/features/announcements/infra/persistence/repositories/sqlalchemy_announcement_repository.py

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.features.announcement.domain.entities.announcement_entity import AnnouncementEntity
from src.features.announcement.domain.repositories.announcement_repository import AnnouncementRepository
from src.features.announcement.infra.persistence.models.announcement_orm import AnnouncementORM
from src.features.announcement.infra.mappers.announcement_mapper import AnnouncementMapper


class AnnouncementRepositoryHandler(AnnouncementRepository):
    """
    SQLAlchemy implementation of the AnnouncementRepository.
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, announcement: AnnouncementEntity) -> AnnouncementEntity:
        """Adds a new announcement to the repository."""
        orm_announcement = AnnouncementMapper.from_entity(announcement)

        self._session.add(orm_announcement)
        await self._session.flush()
        await self._session.refresh(orm_announcement)

        return AnnouncementMapper.to_entity(orm_announcement)

    async def get_by_uid(self, uid: uuid.UUID) -> Optional[AnnouncementEntity]:
        """Retrieves an announcement by its unique identifier."""
        stmt = select(AnnouncementORM).filter_by(uid=uid)
        result = await self._session.execute(stmt)
        orm_announcement = result.scalar_one_or_none()

        return AnnouncementMapper.to_entity(orm_announcement) if orm_announcement else None

    async def get_all(self) -> List[AnnouncementEntity]:
        """Retrieves all announcements, ordered by creation date (newest first)."""
        stmt = select(AnnouncementORM).order_by(AnnouncementORM.created_at.desc())
        result = await self._session.execute(stmt)
        orm_announcements = result.scalars().all()

        return [AnnouncementMapper.to_entity(a) for a in orm_announcements]

    async def update(self, announcement: AnnouncementEntity) -> AnnouncementEntity:
        """Updates an existing announcement."""
        orm_announcement = await self._session.get(AnnouncementORM, announcement.uid)
        if not orm_announcement:
            raise ValueError(f"Announcement with UID {announcement.uid} not found for update.")

        # Update fields from the entity
        orm_announcement.title = announcement.title
        orm_announcement.version = announcement.version
        orm_announcement.text = announcement.text
        orm_announcement.type = announcement.type
        orm_announcement.updated_at = announcement.updated_at  # Manually set for Base model hook

        await self._session.flush()
        await self._session.refresh(orm_announcement)

        return AnnouncementMapper.to_entity(orm_announcement)

    async def delete(self, uid: uuid.UUID) -> None:
        """Deletes an announcement by its unique identifier."""
        orm_announcement = await self._session.get(AnnouncementORM, uid)
        if orm_announcement:
            await self._session.delete(orm_announcement)
            await self._session.flush()