# src/features/prices/application/command_handlers/price_command_handlers.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass

from src.core.base.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator  # For publishing events
from src.features.prices.application.commands.create_platfrom_price_command import CreatePlatformPriceCommand
from src.features.prices.domain.entities.price_entity import PlatformPriceEntity
from src.features.prices.domain.uow.price_unit_of_work import PriceUnitOfWork
from src.features.prices.exceptions.price_exceptions import PlatformPriceAlreadyExistsError




@dataclass
class CreatePlatformPriceCommandHandler(BaseCommandHandler[CreatePlatformPriceCommand, None]):
    """Handles the AddPlatformPriceCommand to add a new platform price."""
    _unit_of_work: PriceUnitOfWork
    _mediator: Mediator

    async def __call__(self, command: CreatePlatformPriceCommand) -> None:
        async with self._unit_of_work as uow:
            # Check if platform already exists
            existing_platform = await uow.platform_price_repository.get_by_service_name(command.service_name)
            if existing_platform:
                raise PlatformPriceAlreadyExistsError(f"Platform with service name '{command.service_name}' already exists.")

            # Create new entity
            new_platform = PlatformPriceEntity(
                service_name=command.service_name,
                price_per_message=command.price_per_message,
                fixed_price=command.fixed_price
            )

            await uow.platform_price_repository.add(new_platform)
            await uow.commit()

            logger.info(f"Platform price for '{command.service_name}' added by user {command.user_uid}.")
            # Optional: Publish an event if downstream systems need to react
            # await self._mediator.publish([PlatformPriceAddedEvent(new_platform.uid, new_platform.service_name, command.user_uid)])

