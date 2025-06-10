# src/features/prices/domain/entities/price_entity.py

import uuid
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, timezone

from src.core.models.base_entity import BaseEntity # Assuming your BaseEntity


@dataclass
class PlatformPriceEntity(BaseEntity):
    """
    Represents the price settings for a specific platform service.
    """
    service_name: str
    price_per_message: float
    fixed_price: float

    def __post_init__(self):
        super().__post_init__()
        if not self.service_name:
            raise ValueError("Service name cannot be empty.")
        if self.price_per_message < 0 or self.fixed_price < 0:
            raise ValueError("Prices cannot be negative.")

    def update_prices(self, price_per_message: float, fixed_price: float):
        """Updates the price values for the platform."""
        if price_per_message < 0 or fixed_price < 0:
            raise ValueError("Prices cannot be negative.")
        self.price_per_message = price_per_message
        self.fixed_price = fixed_price
        self.update_timestamp()