# src/infra/services/s3/application/queries/get_user_avatar_query_handler.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass

from src.core.base.query import BaseQueryHandler
from src.features.identity.api.v1.dtos.profile.get_avatar_dto import GetAvatarResponseDTO
from src.features.identity.domain.repositories.user_unit_of_work import UserUnitOfWork
from src.features.identity.application.queries.profile.get_avatar.get_me_avatar_query import GetMeAvatarQuery
from src.features.identity.exceptions.user_exceptions import UserNotFoundError, AvatarNotFoundError




@dataclass
class GetMeAvatarQueryHandler(BaseQueryHandler[GetMeAvatarQuery, GetAvatarResponseDTO]):
    """
    Handles the GetUserAvatarQuery to retrieve a user's avatar URL from the repository.
    This handler implicitly interacts with the storage layer (via UserUnitOfWork)
    to get the URL which is assumed to be an S3 pre-signed URL or public URL.
    """
    _unit_of_work: UserUnitOfWork

    async def __call__(self, query: GetMeAvatarQuery) -> GetAvatarResponseDTO:
        logger.debug(f"Handling GetUserAvatarQuery for user_uid: {query.user_uid}")

        async with self._unit_of_work as uow:
            user = await uow.user_repository.find_by_uid(query.user_uid)

            if not user:
                logger.warning(f"User not found for UID: {query.user_uid}")
                raise UserNotFoundError(f"User with UID {query.user_uid} not found.")

            if not user.avatar_file_url:
                logger.warning(f"No avatar URL found for user UID: {query.user_uid}")
                raise AvatarNotFoundError(f"No avatar available for user with UID {query.user_uid}.")

            logger.info(f"Retrieved avatar URL for user {query.user_uid}: {user.avatar_file_url}")
            return GetAvatarResponseDTO(avatar_url=user.avatar_file_url)