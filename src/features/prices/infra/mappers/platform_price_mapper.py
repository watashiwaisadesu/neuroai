# src/features/prices/infra/persistence/mappers/price_mappers.py
from src.features.prices.domain.entities.price_entity import PlatformPriceEntity
from src.features.prices.infra.persistence.models.platform_price_orm import PlatformPriceORM


class PlatformPriceMapper:
    """Maps between PlatformPriceEntity and PlatformPriceORM."""

    @staticmethod
    def to_entity(orm_model: PlatformPriceORM) -> PlatformPriceEntity:
        return PlatformPriceEntity(
            uid=orm_model.uid,
            service_name=orm_model.service_name,
            price_per_message=orm_model.price_per_message,
            fixed_price=orm_model.fixed_price,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at
        )

    @staticmethod
    def to_orm(entity: PlatformPriceEntity) -> PlatformPriceORM:
        return PlatformPriceORM(
            uid=entity.uid,
            service_name=entity.service_name,
            price_per_message=entity.price_per_message,
            fixed_price=entity.fixed_price,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )