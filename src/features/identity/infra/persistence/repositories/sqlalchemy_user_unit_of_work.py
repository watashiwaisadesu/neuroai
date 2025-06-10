from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.features.identity.domain.repositories.user_repository import UserRepository
from src.features.identity.domain.repositories.user_unit_of_work import UserUnitOfWork



class SQLAlchemyUserUnitOfWork(UserUnitOfWork):
    def __init__(self, session: AsyncSession, user_repository: UserRepository) -> None:
        self._session: AsyncSession = session
        self.user_repository: UserRepository = user_repository
        logger.debug("PlatformUserUnitOfWorkImpl initialized.")


    async def __aenter__(self):
        await self.begin()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self.commit()
        else:
            print("/")
            await self.rollback()
        await self._session.close()

    async def begin(self) -> None:
        await self._session.begin()

    async def commit(self) -> None:
        # print(f"[DEBUG] Committing session: {id(self._session)}")
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()