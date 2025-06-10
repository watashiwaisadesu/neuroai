# 2. Query Handler (src/features/identity/application/queries/profile/get_me/get_me_query_handler.py)
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass, field

from src.core.base.query import BaseQueryHandler
from src.core.mediator.mediator import Mediator
from src.features.identity.api.v1.dtos.profile.get_me_dto import UserResponseDTO, UserDTO
from src.features.identity.application.queries.profile.get_me.get_me_query import GetMeQuery
from src.features.identity.application.mappers.user_dto_mapper import UserDTOMapper
from src.features.identity.domain.entities.user_entity import UserEntity
from src.features.identity.domain.repositories.user_unit_of_work import UserUnitOfWork
from src.features.identity.exceptions.user_exceptions import UserNotFoundError




@dataclass
class GetMeQueryHandler(BaseQueryHandler[GetMeQuery, UserResponseDTO]):
    _unit_of_work: UserUnitOfWork
    _mediator: Mediator

    _user_dto_mapper: UserDTOMapper = field(init=False, repr=False)

    def __post_init__(self):
        self._user_dto_mapper = UserDTOMapper(UserEntity, UserDTO)

    async def __call__(self, query: GetMeQuery) -> UserResponseDTO:
        async with self._unit_of_work as uow:
            # Fetch user by UID
            user = await uow.user_repository.find_by_uid(query.user_uid)
            if not user:
                raise UserNotFoundError(f"User with UID {query.user_uid} not found")

        # Map to DTO
        user_dto = self._user_dto_mapper.to_dto(user)

        return UserResponseDTO(
            message="User information retrieved successfully.",
            user=UserDTO(**user_dto.model_dump())
        )