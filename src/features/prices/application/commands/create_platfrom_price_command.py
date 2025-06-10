from dataclasses import dataclass
from uuid import UUID

from src.core.mediator.command import BaseCommand  # Assuming your BaseCommand


@dataclass
class CreatePlatformPriceCommand(BaseCommand):
    """Command to add a new platform price."""
    service_name: str
    price_per_message: float
    fixed_price: float
    user_uid: UUID # Context for security/auditing


