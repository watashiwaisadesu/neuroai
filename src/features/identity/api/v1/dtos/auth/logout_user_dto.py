from pydantic import BaseModel

from src.features.identity.api.v1.dtos.auth.login_user_dto import MinimalUserDTO


class LogoutUserRequestDTO(BaseModel):
    jti: str

class LogoutUserResponseDTO(BaseModel):
    message: str = "Logged Out Successfully"
    user: MinimalUserDTO
