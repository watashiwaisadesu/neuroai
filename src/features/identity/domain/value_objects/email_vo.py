# src/features/identity/domain/value_objects/email_vo.py
import re
from dataclasses import dataclass

class InvalidEmailError(ValueError):
    """Custom exception for invalid email format."""
    pass

@dataclass(frozen=True) # frozen=True makes it immutable
class Email:
    value: str

    def __post_init__(self):
        # Basic email validation regex
        # This regex is a simplification and might not cover all edge cases
        # but is a good starting point without Pydantic.
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.fullmatch(email_regex, self.value):
            raise InvalidEmailError(f"'{self.value}' is not a valid email address.")

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other) -> bool:
        if isinstance(other, Email):
            return self.value == other.value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.value)