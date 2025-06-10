from pydantic import BaseModel, EmailStr
from uuid import UUID


class RequestChangeEmailRequestDTO(BaseModel):
    new_email: EmailStr


class RequestChangeEmailInputDTO(BaseModel):
    user_uid: UUID
    new_email: EmailStr


class RequestChangeEmailResponseDTO(BaseModel):
    message: str