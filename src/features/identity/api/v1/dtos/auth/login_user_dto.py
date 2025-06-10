from uuid import UUID

from pydantic import EmailStr, BaseModel


class MinimalUserDTO(BaseModel):
    email: str
    uid: UUID
    role: str

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

