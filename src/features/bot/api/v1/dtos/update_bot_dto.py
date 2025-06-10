from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID


class UpdateBotRequestDTO(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    temperature: Optional[float] = None
    crm_lead_id: Optional[int] = None
    token_limit: Optional[int] = None
    auto_deduction: Optional[bool] = None
    max_response: Optional[int] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    repetition_penalty: Optional[float] = None
    generation_model: Optional[str] = None

class UpdateBotInputDTO(BaseModel):
    uid: UUID
    data: UpdateBotRequestDTO

