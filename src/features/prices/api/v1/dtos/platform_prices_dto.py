from pydantic import BaseModel, Field
from typing import List, Optional


# Request DTOs
class PlatformRequestDTO(BaseModel):
    service_name: str = Field(..., example="example_platform")
    price_per_message: float = Field(..., ge=0.0, example=0.01)
    fixed_price: float = Field


# Response DTOs
class PlatformDTO(BaseModel):
    service_name: str
    price_per_message: float
    fixed_price: float

class PlatformResponseDTO(BaseModel):
    message: str
    platform: PlatformDTO

class GetPlatformsResponseDTO(BaseModel):
    message: str
    platforms: List[PlatformDTO]