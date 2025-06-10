from typing import Sequence, List
from uuid import UUID
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger

from sqlalchemy import select, update as sqlalchemy_update, delete as sqlalchemy_delete
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.features.identity.domain.entities.user_entity import UserEntity
from src.features.identity.domain.repositories.user_repository import UserRepository
from src.features.identity.domain.value_objects.email_vo import Email
from src.features.identity.infra.mappers.user_mapper import UserMapper
from src.features.identity.infra.persistence.models.user import UserORM





class SQlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session
        self._mapper = UserMapper(UserEntity, UserORM)

    async def find_by_email(self, email: str) -> UserEntity | None:
        statement = select(UserORM).filter_by(email=email)
        try:
            result = await self._session.execute(statement)
            orm_obj = result.scalar_one()
            return self._mapper.to_entity(orm_obj)
        except NoResultFound:
            return None

    async def create(self, entity: UserEntity) -> UserEntity:
        orm_obj = self._mapper.from_entity(entity)
        self._session.add(orm_obj)
        # print(f"[DEBUG] Session ID: {id(self._session)}")
        await self._session.flush()
        return self._mapper.to_entity(orm_obj)

    async def findall(self) -> Sequence[UserEntity]:
        statement = select(UserORM)
        result = await self._session.execute(statement)
        orm_users: Sequence[UserORM] = result.scalars().all()
        return [self._mapper.to_entity(user) for user in orm_users]

    async def find_by_uid(self, uid: UUID) -> UserEntity | None:
        stmt = select(UserORM).where(UserORM.uid == uid)
        result = await self._session.execute(stmt)
        orm_obj = result.scalar_one_or_none()
        if orm_obj:
            return self._mapper.to_entity(orm_obj)  # Map ORM to Entity
        return None

    async def update(self, entity: UserEntity) -> UserEntity:
        orm_obj = self._mapper.from_entity(entity)
        update_data = orm_obj.__dict__.copy()

        # Удаляем служебные поля
        update_data.pop("_sa_instance_state", None)
        update_data.pop("created_at", None)
        update_data.pop("uid", None)

        statement = (
            sqlalchemy_update(UserORM)
            .where(UserORM.uid == orm_obj.uid)
            .values(update_data)
            .returning(UserORM)
        )

        result = await self._session.execute(statement)
        row = result.fetchone()
        if not row:
            raise ValueError(f"User with uid={orm_obj.uid} not found")

        return self._mapper.to_entity(row[0])

    async def delete_by_uid(self, uid: UUID) -> None:
        statement = (
            sqlalchemy_delete(UserORM)
            .where(UserORM.uid == uid)
        )
        await self._session.execute(statement)

    async def find_by_uids(self, uids: List[UUID]) -> List[UserEntity]:
        """Finds multiple users by their UIDs using an IN clause."""
        if not uids:
            return []  # Return empty list if no UIDs provided

        logger.debug(f"Finding users by UIDs: {uids}")
        statement = select(UserORM).where(UserORM.uid.in_(uids))
        try:
            result = await self._session.execute(statement)
            orm_results = result.scalars().all()
            # Ensure mapper handles None correctly or filter
            entities = [self._mapper.to_entity(orm_obj) for orm_obj in orm_results if orm_obj]
            logger.debug(f"Found {len(entities)} users for {len(uids)} requested UIDs.")
            return entities
        except Exception as e:
            logger.error(f"Error finding users by UIDs: {e}", exc_info=True)
            return []  # Return empty list on error or re-raise
