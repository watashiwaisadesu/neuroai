import uuid
from dataclasses import dataclass, field
from typing import Optional

# --- Value Objects ---
# These describe characteristics, have no identity of their own within the aggregate,
# and are typically immutable (or treated as such).

@dataclass(frozen=True) # frozen=True makes it immutable (good for VOs)
class AIConfigurationSettings:
    """Holds the AI configuration settings."""
    instructions: Optional[str] = None
    temperature: float = 0.5
    top_p: float = 0.9
    top_k: int = 40
    max_response: int = 250
    repetition_penalty: float = 0.0
    generation_model: str = "deepseek-v2:16b"

    def __post_init__(self):
        # Example Validation within the Value Object itself
        if not (0.0 <= self.temperature <= 1.0):
            raise ValueError("Temperature must be between 0.0 and 1.0")
        if self.max_response <= 0:
            raise ValueError("Max response must be positive")
        # ... other validations ...
