from pydantic import Field, EmailStr, BaseModel
from uuid import UUID


class MinimalUserDTO(BaseModel):
    email: str
    uid: UUID
    role: str
    is_verified: bool

class TokenDTO(BaseModel):
    access_token: str
    refresh_token: str


class LoginUserRequestDTO(BaseModel):
    email: EmailStr
    password: str


class TokenResponseDTO(BaseModel):
    message: str
    tokens: TokenDTO
    user: MinimalUserDTO

