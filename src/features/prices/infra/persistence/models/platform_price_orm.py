
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID

from src.infra.persistence.models.sqlalchemy_base import SQLAlchemyBase


class PlatformPriceORM(SQLAlchemyBase):
    """SQLAlchemy ORM model for platform price settings."""
    __tablename__ = "platform_prices"

    service_name = Column(String, unique=True, nullable=False)
    price_per_message = Column(Float, nullable=False)
    fixed_price = Column(Float, nullable=False)

    def __repr__(self):
        return f"<PlatformPrice(service_name='{self.service_name}', price_per_message={self.price_per_message})>"
