# src/infra/services/s3/application/dtos/avatar_response_dto.py
from pydantic import BaseModel, Field

class GetAvatarResponseDTO(BaseModel):
    """
    DTO for the response containing the user's avatar URL.
    """
    avatar_url: str = Field(..., description="The public URL of the user's avatar.")