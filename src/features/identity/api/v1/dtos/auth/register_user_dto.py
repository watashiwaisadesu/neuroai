from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, model_validator, EmailStr


class RegisterUserDTO(BaseModel):
    phone_number: Optional[str] = None
    company_name: Optional[str] = None
    field_of_activity: Optional[str] = None
    BIN: Optional[str] = None
    legal_address: Optional[str] = None
    contact: Optional[str] = None
    registration_date: Optional[date] = None


class RegisterUserRequestDTO(RegisterUserDTO):
    user_type: str = Field(..., description="Can be 'individual or 'legal_entity'")
    email: EmailStr = Field(..., max_length=40)
    password: str = Field(..., min_length=6, max_length=25)
    is_send_docs_to_jur_address: Optional[bool] = None

    @model_validator(mode="after")
    def validate_create(self) -> "RegisterUserRequestDTO":
        if self.user_type not in ("individual", "legal_entity"):
            raise ValueError("Invalid user_type. Must be 'individual' or 'legal_entity'.")

        if self.user_type == "individual":
            for field in [
                "phone_number", "company_name", "field_of_activity",
                "BIN", "legal_address", "contact", "registration_date",
                "is_send_docs_to_jur_address"
            ]:
                setattr(self, field, None)

        elif self.user_type == "legal_entity":
            if self.is_send_docs_to_jur_address:
                for field in [
                    "company_name", "field_of_activity", "BIN",
                    "legal_address", "contact", "phone_number"
                ]:
                    if not getattr(self, field):
                        raise ValueError(f"{field} is required when is_send_docs_to_jur_address is True")
            else:
                for field in ["BIN", "legal_address", "contact", "phone_number"]:
                    setattr(self, field, None)

            if self.registration_date is None:
                self.registration_date = date.today()

        return self





