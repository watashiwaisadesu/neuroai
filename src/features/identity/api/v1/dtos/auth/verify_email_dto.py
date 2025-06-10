from pydantic import BaseModel

from src.features.identity.api.v1.dtos.auth.login_user_dto import MinimalUserDTO


class VerifyEmailResponseDTO(BaseModel):
    message: str
    user: MinimalUserDTO
