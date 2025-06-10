from dataclasses import dataclass, field
from typing import Optional
from datetime import date

@dataclass(frozen=True, kw_only=True)
class CompanyDetails:
    company_name: Optional[str] = None
    field_of_activity: Optional[str] = None
    is_send_docs_to_jur_address: Optional[bool] = None
    BIN: Optional[str] = None
    legal_address: Optional[str] = None
    contact: Optional[str] = None
    phone_number: Optional[str] = None
    registration_date: Optional[date] = None

    def __post_init__(self):
        """Validate company details if needed"""
        # Add any validation logic here if required
        pass

    def has_complete_info(self) -> bool:
        """Check if all essential company information is provided"""
        essential_fields = [
            self.company_name,
            self.BIN,
            self.legal_address,
            self.contact,
            self.phone_number
        ]
        return all(field is not None and field.strip() != "" for field in essential_fields if isinstance(field, str))

    def is_empty(self) -> bool:
        """Check if the company details are essentially empty"""
        return not any([
            self.phone_number,
            self.company_name,
            self.field_of_activity,
            self.BIN,
            self.legal_address,
            self.contact,
            self.registration_date
        ])