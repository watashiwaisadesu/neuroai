
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.features.prices.domain.entities.price_entity import PlatformPriceEntity
from src.features.prices.domain.repositories.price_repository import PlatformPriceRepository
from src.features.prices.infra.mappers.platform_price_mapper import PlatformPriceMapper
from src.features.prices.infra.persistence.models.platform_price_orm import PlatformPriceORM


class SQLAlchemyPlatformPriceRepository(PlatformPriceRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, entity: PlatformPriceEntity) -> None:
        orm_obj = PlatformPriceMapper.to_orm(entity)
        self._session.add(orm_obj)
        await self._session.flush() # Flush to assign primary key if entity.uid is not pre-assigned

    async def get_by_service_name(self, service_name: str) -> Optional[PlatformPriceEntity]:
        query = select(PlatformPriceORM).where(PlatformPriceORM.service_name == service_name)
        result = await self._session.execute(query)
        orm_obj = result.scalars().first()
        if orm_obj:
            return PlatformPriceMapper.to_entity(orm_obj)
        return None

    async def get_all(self) -> List[PlatformPriceEntity]:
        query = select(PlatformPriceORM).order_by(PlatformPriceORM.service_name)
        result = await self._session.execute(query)
        return [PlatformPriceMapper.to_entity(orm_obj) for orm_obj in result.scalars().all()]

    async def update(self, entity: PlatformPriceEntity) -> None:
        orm_obj = await self._session.get(PlatformPriceORM, entity.uid)
        if not orm_obj:
            raise ValueError(f"Platform price with UID {entity.uid} not found for update.")
        # Update fields
        orm_obj.service_name = entity.service_name
        orm_obj.price_per_message = entity.price_per_message
        orm_obj.fixed_price = entity.fixed_price
        # updated_at will be handled by ORM's onupdate
        await self._session.flush()


    async def delete(self, uid: UUID) -> None:
        orm_obj = await self._session.get(PlatformPriceORM, uid)
        if orm_obj:
            await self._session.delete(orm_obj)
            await self._session.flush()
