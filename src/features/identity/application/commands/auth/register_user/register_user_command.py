from dataclasses import dataclass
from datetime import date
from typing import Optional

from src.core.base.command import BaseCommand


@dataclass
class RegisterUserCommand(BaseCommand):
    email: str
    password: str
    user_type: str

    is_send_docs_to_jur_address: Optional[bool] = None
    phone_number: Optional[str] = None
    company_name: Optional[str] = None
    field_of_activity: Optional[str] = None
    BIN: Optional[str] = None
    legal_address: Optional[str] = None
    contact: Optional[str] = None
    registration_date: Optional[date] = None