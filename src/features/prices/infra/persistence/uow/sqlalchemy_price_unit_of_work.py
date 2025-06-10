# src/features/prices/infra/persistence/uow/sqlalchemy_price_unit_of_work.py

from sqlalchemy.ext.asyncio import AsyncSession

from src.features.prices.domain.uow.price_unit_of_work import PriceUnitOfWork
from src.features.prices.infra.mappers.platform_price_mapper import PlatformPriceMapper
from src.features.prices.infra.persistence.repositories.sqlalchemy_platform_price_repositories import \
    SQLAlchemyPlatformPriceRepository


class SQLAlchemyPriceUnitOfWork(PriceUnitOfWork):
    def __init__(self, session: AsyncSession, platform_price_repository: SQLAlchemyPlatformPriceRepository):
        self._session = session
        self.platform_price_repository =platform_price_repository

    async def __aenter__(self):
        # Session is typically managed externally (e.g., FastAPI dependency)
        # but the UoW can be responsible for its lifecycle if created within UoW
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        # Session closure/release is handled by the get_async_db dependency in FastAPI
        # await self._session.close() # Only if UoW is responsible for session creation/closure

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()

