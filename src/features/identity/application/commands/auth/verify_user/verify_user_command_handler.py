from dataclasses import dataclass, field

from src.core.base.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.core.utils.hashing import decode_url_safe_token
from src.features.identity.api.v1.dtos.profile.get_me_dto import UserResponseDTO, UserDTO
from src.features.identity.application.commands.auth.verify_user.verify_user_command import VerifyUserCommand
from src.features.identity.application.mappers.user_dto_mapper import UserDTOMapper
from src.features.identity.domain.entities.user_entity import UserEntity
from src.features.identity.domain.repositories.user_unit_of_work import UserUnitOfWork
from src.features.identity.exceptions.auth_exceptions import InvalidTokenError, AuthVerificationError
from src.features.identity.exceptions.user_exceptions import UserNotFoundError

@dataclass
class VerifyUserCommandHandler(BaseCommandHandler[VerifyUserCommand, UserResponseDTO]):
    _unit_of_work: UserUnitOfWork
    _mediator: Mediator

    _user_mapper: UserDTOMapper = field(init=False, repr=False)

    def __post_init__(self):
        print("a")
        self._user_mapper = UserDTOMapper(UserEntity, UserDTO)
        print("a")

    async def __call__(self, command: VerifyUserCommand) -> UserResponseDTO:
        try:
            print("a")
            token_data = decode_url_safe_token(command.token)
            email = token_data.get("email")
            print(email)
            if not email:
                raise InvalidTokenError()

            user = await self._unit_of_work.user_repository.find_by_email(email)
            print(user)
            if not user:
                raise UserNotFoundError()

            user.verify()
            user = await self._unit_of_work.user_repository.update(user)
            await self._unit_of_work.commit()

            print("ttt")
            user_dto = self._user_mapper.to_dto(user)

            return UserResponseDTO(
                message="Account verified successfully.",
                user=UserDTO(**user_dto.model_dump())
            )
        except (InvalidTokenError, UserNotFoundError):
            raise
        except Exception:
            await self._unit_of_work.rollback()
            raise AuthVerificationError()
