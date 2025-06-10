from fastapi import UploadFile
from pydantic import BaseModel

from src.features.identity.domain.entities.user_entity import UserEntity


class UpdateAvatarInputDTO(BaseModel):
    avatar: UploadFile
    user: UserEntity

    class Config:
        arbitrary_types_allowed = True


class AvatarUploadResponseDTO(BaseModel):
    message: str
    request_id: str
    status: str = "processing"


