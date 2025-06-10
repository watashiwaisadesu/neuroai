# src/features/bot/api/dtos/bot_service_management_dto.py (New file or add to existing DTO file)

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from pydantic import BaseModel, Field
from typing import List

from src.features.bot.api.v1.dtos.bot_service_dto import BotServiceDTO

from enum import Enum
class ServicePlatform(str, Enum):
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    INSTAGRAM = "instagram"
    # ... other platforms



# --- DTO for Linking a Service (Request Body) ---
class LinkServiceRequestDTO(BaseModel):
    """Data needed to link a service platform to a bot."""
    platform: ServicePlatform =Field(..., description="Name of the platform/service to link (e.g., 'telegram', 'whatsapp').", min_length=1)


# --- DTO for Service Details (Used in Responses) ---
class LinkServiceResponseDTO(BaseModel): # Renamed from just `BotServiceResponseItemDTO` to be the wrapper
    """API response DTO for a single bot service operation."""
    message: str = Field(..., description="A descriptive message about the operation result.")
    service: BotServiceDTO = Field(..., description="Details of the bot service.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Service 'telegram' successfully linked to bot.",
                "service": {
                    "service_uid": "e1f2a3b4-c5d6-7890-1234-fedcba987654",
                    "bot_uid": "b1c2d3e4-f5a6-7890-1234-abcdef123456",
                    "platform": "telegram",
                    "status": "active",
                    "linked_account_uid": "f1e2d3c4-b5a6-7890-1234-abcdef123456"
                }
            }
        }
    }

class GetServicesResponseDTO(BaseModel):
    message: str
    services: List[BotServiceDTO]

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Successfully retrieved 2 services for bot.",
                "services": [
                    {
                        "service_uid": "e1f2a3b4-c5d6-7890-1234-fedcba987654",
                        "bot_uid": "b1c2d3e4-f5a6-7890-1234-abcdef123456",
                        "platform": "telegram",
                        "status": "active",
                        "linked_account_uid": "f1e2d3c4-b5a6-7890-1234-abcdef123456"
                    },
                    {
                        "service_uid": "f1g2h3i4-j5k6-7890-1234-fedcba987654",
                        "bot_uid": "b1c2d3e4-f5a6-7890-1234-abcdef123456",
                        "platform": "discord",
                        "status": "reserved",
                        "linked_account_uid": None
                    }
                ]
            }
        }
    }

class UnlinkServiceResponseDTO(BaseModel):
    message: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Service successfully unlinked from bot."
            }
        }
    }



