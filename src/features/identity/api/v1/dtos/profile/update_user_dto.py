from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class UserUpdateRequestDTO(BaseModel):
    phone_number: Optional[str] = None
    company_name: Optional[str] = None
    field_of_activity: Optional[str] = None
    BIN: Optional[str] = None
    legal_address: Optional[str] = None
    contact: Optional[str] = None
    registration_date: Optional[date] = None
    user_type: str = Field(...)

