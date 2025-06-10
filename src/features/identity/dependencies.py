# Standard Library Imports
from typing import List

# FastAPI Imports
from fastapi import Depends, Security
# --- Shared Infrastructure Imports ---
# (Assuming these top-level infra paths are correct)
from sqlalchemy.ext.asyncio import AsyncSession

# Project Configuration
from src.config import Settings  # Assuming this path is still correct

from src.features.identity.application.queries.profile.get_me.get_me_query import GetMeQuery
# Domain Layer - Services
from src.features.identity.application.services.token_blocklist_service import TokenBlocklistService
from src.features.identity.application.services.token_service import TokenService
# Domain Layer - Entities
from src.features.identity.domain.entities.user_entity import UserEntity  # Renamed & Moved
# Domain Layer - Repositories (Interfaces)
# Assuming you renamed UserRepository -> PlatformUserRepository and PlatformUserUnitOfWork -> PlatformPlatformUserUnitOfWork
from src.features.identity.domain.repositories.user_repository import UserRepository  # Renamed interface
from src.features.identity.domain.repositories.user_unit_of_work import UserUnitOfWork  # Renamed interface
# Feature Specific Exceptions (Moved)
from src.features.identity.exceptions.auth_exceptions import InvalidTokenError  # Renamed folder
# Infrastructure Layer - Persistence (Implementations)
# Assuming you renamed UserRepositoryImpl -> SqlAlchemyPlatformUserRepository and PlatformUserUnitOfWorkImpl -> PlatformPlatformUserUnitOfWorkImpl
from src.features.identity.infra.persistence.repositories.sqlalchemy_user_repository import \
    SQlAlchemyUserRepository  # Renamed implementation
from src.features.identity.infra.persistence.repositories.sqlalchemy_user_unit_of_work import \
    SQLAlchemyUserUnitOfWork  # Renamed implementation
# Infrastructure Layer - Security (Moved)
from src.features.identity.infra.security.role_checker import RoleChecker
from src.features.identity.infra.security.token_bearer import AccessTokenBearer, RefreshTokenBearer
# Infrastructure Layer - Services (Implementations)
from src.features.identity.infra.services.token_blocklist_service_handler import TokenBlocklistServiceHandler
from src.features.identity.infra.services.token_service_handler import TokenServiceHandler
from src.infra.persistence.connection.sqlalchemy_engine import get_async_db
from src.infra.services.redis.redis_service_handler import RedisServiceHandler

# --- Identity Feature Imports ---


settings: Settings = Settings()

async def get_user_repository( # Function possibly renamed
    session: AsyncSession = Depends(get_async_db),
) -> UserRepository: # Use renamed interface
    return SQlAlchemyUserRepository(session) # Use renamed implementation

async def get_user_unit_of_work( # Function possibly renamed
    session: AsyncSession = Depends(get_async_db),
) -> UserUnitOfWork: # Use renamed interface
    repository = await get_user_repository(session) # Use updated dependency
    return SQLAlchemyUserUnitOfWork(session, repository) # Use renamed implementation

def get_token_service() -> TokenService:
    return TokenServiceHandler(
        secret_key=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
        access_token_expiry=settings.ACCESS_TOKEN_EXPIRY_MINUTES,
        refresh_token_expiry=settings.REFRESH_TOKEN_EXPIRY_DAYS,
    )


def get_token_blocklist_service() -> TokenBlocklistService:
    return TokenBlocklistServiceHandler(RedisServiceHandler())


def get_access_token_bearer() -> AccessTokenBearer:
    print("Aaaa")
    return AccessTokenBearer(
        token_service=get_token_service(),
        blocklist_service=get_token_blocklist_service(),
    )

def get_refresh_token_bearer() -> RefreshTokenBearer:
    return RefreshTokenBearer(
        token_service=get_token_service(),
        blocklist_service=get_token_blocklist_service(),
    )

async def get_current_user(
    token_details: dict = Security(get_access_token_bearer()),
    uow: UserUnitOfWork = Depends(get_user_unit_of_work),
):
    user_email = token_details["user"]["email"]
    user = await uow.user_repository.find_by_email(user_email)
    if not user:
        raise InvalidTokenError()
    return user

def get_role_checker(allowed_roles: List[str]):
    """
    Factory function that returns a dependency check function (_check).
    The returned _check function verifies if the current user has one of the allowed roles.
    """
    # Create an instance of the checker class with the allowed roles
    checker = RoleChecker(allowed_roles)

    # Define the actual dependency function that FastAPI will call
    def _check(current_user: UserEntity = Depends(get_current_user)):
        """
        This inner function is the actual dependency.
        It gets the current user and uses the checker instance to validate the role.
        The checker raises an exception if the role is not allowed.
        """
        # checker.__call__(current_user) will raise HTTPException if not allowed
        checker(current_user)
        # If no exception is raised, the dependency is satisfied.
        # We don't strictly need to return anything meaningful here.
        # Returning True or None is fine.
        return True

    # Return the inner function ITSELF, not Depends(inner_function)
    return _check
############################################################################
############################################################################
############################################################################







