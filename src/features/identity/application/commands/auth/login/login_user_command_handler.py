from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass, field

from src.config import Settings
from src.core.base.command import BaseCommandHandler  # Assuming you have this base command handler
from src.core.mediator.mediator import Mediator  # Assuming you have this mediator
from src.core.utils.hashing import verify_password
from src.features.identity.api.v1.dtos.auth.login_user_dto import TokenResponseDTO, \
    TokenDTO, MinimalUserDTO
from src.features.identity.application.commands.auth.login.login_user_command import LoginUserCommand
from src.features.identity.application.mappers.minimal_user_dto_mapper import MinimalUserDTOMapper
from src.features.identity.application.services.token_service import TokenService
from src.features.identity.domain.entities.user_entity import UserEntity
from src.features.identity.domain.repositories.user_unit_of_work import UserUnitOfWork
from src.features.identity.exceptions.auth_exceptions import (
    AccountNotVerifiedError,
    InvalidCredentialsError
)
from src.features.identity.exceptions.user_exceptions import (
    UserNotFoundError
)



@dataclass
class LoginUserCommandHandler(BaseCommandHandler[LoginUserCommand, TokenResponseDTO]):
    _unit_of_work: UserUnitOfWork
    _token_service: TokenService
    _mediator: Mediator

    _settings: Settings
    _minimal_user_dto_mapper: MinimalUserDTOMapper = field(init=False, repr=False)

    def __post_init__(self):
        self._minimal_user_dto_mapper = MinimalUserDTOMapper(UserEntity, MinimalUserDTO)


    async def __call__(self, command: LoginUserCommand) -> TokenResponseDTO:
        user = await self._unit_of_work.user_repository.find_by_email(command.email)
        if user is None:
            logger.warning(f"Login attempt for non-existent email: {command.email}")
            raise UserNotFoundError()

        if not user.is_verified:
            logger.warning(f"Login attempt for unverified account: {command.email}")
            raise AccountNotVerifiedError()

        if not verify_password(command.password, user.password_hash):
            logger.warning(f"Login attempt with invalid credentials for user: {command.email}")
            raise InvalidCredentialsError()

        new_access_token = self._token_service.create_access_token({
            "email": user.email,
            "user_uid": str(user.uid),
            "role": user.role,
        })

        new_refresh_token = self._token_service.create_refresh_token({
            "email": user.email,
            "user_uid": str(user.uid),
            "role": user.role,
        })

        user_dto = self._minimal_user_dto_mapper.to_dto(user)

        return TokenResponseDTO(
            message="User logged in successfully.",
            tokens=TokenDTO(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
            ),
            user=MinimalUserDTO(**user_dto.model_dump())
        )