from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import field, dataclass
from typing import Optional

from src.core.base.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.core.utils.hashing import hash_password
from src.features.identity.api.v1.dtos.profile.get_me_dto import UserResponseDTO, UserDTO
from src.features.identity.application.commands.auth.register_user.register_user_command import RegisterUserCommand
from src.features.identity.application.mappers.user_dto_mapper import UserDTOMapper
from src.features.identity.domain.entities.user_entity import UserEntity
from src.features.identity.domain.repositories.user_unit_of_work import UserUnitOfWork
from src.features.identity.domain.value_objects.company_details_vo import CompanyDetails
from src.features.identity.exceptions.user_exceptions import UserAlreadyExistsError





@dataclass
class RegisterUserCommandHandler(BaseCommandHandler[RegisterUserCommand, UserResponseDTO]):
    _unit_of_work: UserUnitOfWork
    _mediator: Mediator

    _user_dto_mapper: UserDTOMapper = field(init=False, repr=False)

    def __post_init__(self):
        self._user_dto_mapper = UserDTOMapper(UserEntity, UserDTO)

    async def __call__(self, command: RegisterUserCommand) -> UserResponseDTO:
        hashed_password = hash_password(command.password)

        company_details = self._create_company_details_if_needed(command=command)

        user_entity = UserEntity.register(
            email=command.email,
            password_hash=hashed_password,
            user_type=command.user_type,
            role=getattr(command, 'role', 'user'),
            company_details=company_details,
        )

        async with self._unit_of_work as uow:
            existing_user = await uow.user_repository.find_by_email(user_entity.email)
            if existing_user:
                raise UserAlreadyExistsError(message=f"User with email {user_entity.email} already exists.")
            await uow.user_repository.create(user_entity)

        events_to_publish = user_entity.pull_events()
        if events_to_publish:
            await self._mediator.publish(events_to_publish)

        mapped_user_dto = self._user_dto_mapper.to_dto(user_entity)
        return UserResponseDTO(
            message="Account created successfully. Please verify your email to verify your account.",
            user=UserDTO(**mapped_user_dto.model_dump())
        )



    @staticmethod
    def _create_company_details_if_needed(command: RegisterUserCommand) -> Optional[CompanyDetails]:
        """Create CompanyDetails value object if user is legal entity"""
        if command.user_type != 'legal_entity':
            return None

        # Only create CompanyDetails if we have at least some company data
        if not any([
            command.phone_number,
            command.company_name,
            command.field_of_activity,
            command.BIN,
            command.legal_address,
            command.contact,
            command.registration_date
        ]):
            return None

        return CompanyDetails(
            phone_number=command.phone_number,
            company_name=command.company_name,
            field_of_activity=command.field_of_activity,
            BIN=command.BIN,
            legal_address=command.legal_address,
            contact=command.contact,
            registration_date=command.registration_date,
            is_send_docs_to_jur_address=getattr(command, 'is_send_docs_to_jur_address', None)
        )

