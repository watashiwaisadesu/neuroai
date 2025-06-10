from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime, date
from typing import Optional

class UserDTO(BaseModel):
    uid: UUID
    email: EmailStr
    role: str
    is_verified: bool
    user_type: Optional[str]
    company_name: Optional[str]
    field_of_activity: Optional[str]
    BIN: Optional[str]
    legal_address: Optional[str]
    contact: Optional[str]
    phone_number: Optional[str]
    registration_date: Optional[date]
    avatar_file_url: Optional[str]
    crm_catalog_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {  # Pydantic v2 uses model_config
        "json_schema_extra": {
            "example": {
                "uid": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "role": "user",
                "is_verified": False,
                "user_type": "individual",
                "is_send_docs_to_jur_address": None,
                "company_name": None,
                "field_of_activity": None,
                "BIN": None,
                "legal_address": None,
                "contact": "John Doe",
                "phone_number": "+1234567890",
                "registration_date": None,
                "crm_catalog_id": 12345,
                "avatar_file_url": "https://example.com/avatar.jpg"
            }
        },
        "from_attributes": True  # Keep this for model_validate compatibility
    }


class UserResponseDTO(BaseModel):
    message: str
    user: UserDTO