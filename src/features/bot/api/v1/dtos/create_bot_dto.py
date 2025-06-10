# create_bot_consultant_dto.py

from pydantic import BaseModel, Field

from src.features.bot.api.v1.dtos.minimal_bot_dto import MinimalBotDTO
from src.features.bot.domain.enums import BotType


class CreateBotRequestDTO(BaseModel):
    bot_type: BotType = Field(..., description=f"The type of bot to create. Allowed types: {', '.join(BotType.list())}")

    model_config = {  # Pydantic v2
        "json_schema_extra": {
            "example": {
                "bot_type": "seller"  # Example uses a valid Enum value
            }
        }
    }

class CreateBotResponseDTO(BaseModel):
    message: str
    bot: MinimalBotDTO












# class CreateBotRequestDTO(BaseModel):
#     name: Optional[str]
#     description: Optional[str]
#     instructions: Optional[str]
#     temperature: Optional[confloat(ge=0.0, le=1.0)]
#     token_limit: Optional[conint(ge=100, le=500000)]
#     auto_deduction: Optional[bool]
#     max_response: Optional[conint(ge=1, le=100000)]
#     top_p: Optional[confloat(ge=0.0, le=1.0)]
#     top_k: Optional[conint(ge=1, le=10000)]
#     repetition_penalty: Optional[confloat(ge=0.0, le=10.0)]
#     bot_services: Optional[List[Literal["telegram", "whatsapp", "instagram"]]] = []
#
# class CreateBotResponseDTO(BaseModel):
#     uid: UUID
#     message: str
#
# class CreateBotInputDTO(BaseModel):
#     user: UserEntity
#     data: CreateBotRequestDTO
#
#     class Config:
#         arbitrary_types_allowed = True
