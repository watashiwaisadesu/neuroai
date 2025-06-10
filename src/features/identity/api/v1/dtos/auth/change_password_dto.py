# src/features/auth/api/dtos/password_change_dto.py

from pydantic import BaseModel, Field

from src.features.identity.api.v1.dtos.auth.login_user_dto import MinimalUserDTO
from src.features.identity.domain.entities.user_entity import UserEntity


class ChangePasswordDTO(BaseModel):
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)
    confirm_new_password: str = Field(..., min_length=6)


class ChangePasswordInputDTO(BaseModel):
    password_data: ChangePasswordDTO
    current_user: UserEntity

    class Config:
        arbitrary_types_allowed = True


class ChangePasswordResponseDTO(BaseModel):
    message: str
    user: MinimalUserDTO
