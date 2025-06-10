# src/features/prices/application/query_handlers/price_query_handlers.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass
from typing import List

from src.core.mediator.mediator import Mediator
from src.core.mediator.query import BaseQueryHandler
from src.features.prices.api.v1.dtos.platform_prices_dto import PlatformDTO, GetPlatformsResponseDTO
from src.features.prices.application.queries.get_platform_prices_query import GetPlatformPricesQuery
from src.features.prices.domain.entities.price_entity import PlatformPriceEntity
from src.features.prices.domain.uow.price_unit_of_work import PriceUnitOfWork




@dataclass
class GetPlatformPricesQueryHandler(BaseQueryHandler[GetPlatformPricesQuery, GetPlatformsResponseDTO]):
    """Handles GetPlatformPricesQuery to retrieve all platform price settings."""
    _unit_of_work: PriceUnitOfWork
    _mediator: Mediator

    async def __call__(self, query: GetPlatformPricesQuery) -> GetPlatformsResponseDTO:
        logger.info(f"Fetching all platform prices for user {query.user_uid}.")
        async with self._unit_of_work as uow:
            platform_entities: List[PlatformPriceEntity] = await uow.platform_price_repository.get_all()

        # Map entities to DTOs
        platform_dtos = [
            PlatformDTO(
                service_name=p.service_name,
                price_per_message=p.price_per_message,
                fixed_price=p.fixed_price
            ) for p in platform_entities
        ]
        logger.info(f"Found {len(platform_dtos)} platform prices.")
        response = GetPlatformsResponseDTO(
                message="Platforms queried successfully", # Use DTO value
                platforms=platform_dtos
            )
        return response

