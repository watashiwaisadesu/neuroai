# src/features/prices/api/routers/price_routes.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from src.core.mediator.mediator import Mediator
from src.features.identity.dependencies import get_current_user
from src.features.identity.domain.entities.user_entity import UserEntity
from src.features.prices.api.v1.dtos.platform_prices_dto import PlatformDTO, PlatformRequestDTO, PlatformResponseDTO
from src.features.prices.application.commands.create_platfrom_price_command import CreatePlatformPriceCommand
from src.features.prices.exceptions.price_exceptions import ( # Your custom exceptions
    PlatformPriceAlreadyExistsError, PriceNegativeError
)



create_price_router = APIRouter()


@create_price_router.post(
    "/",
    response_model=PlatformResponseDTO, # Changed to return the created platform info
    status_code=status.HTTP_201_CREATED,
    summary="Add a new platform pricing configuration (Admin only)"
)
@inject
async def create_platform_price(
    platform_data: PlatformRequestDTO,
    mediator: Mediator = Depends(Provide["mediator"]),
    current_user: UserEntity = Depends(get_current_user),
):
    """
    Adds a new platform service with its pricing details.
    Requires 'admin' role.
    """
    command = CreatePlatformPriceCommand(
        service_name=platform_data.service_name,
        price_per_message=platform_data.price_per_message,
        fixed_price=platform_data.fixed_price,
        user_uid=current_user.uid # Pass user for context/auditing
    )
    try:
        await mediator.execute(command)
        logger.info(f"Platform '{platform_data.service_name}' added by admin {current_user.uid}.")
        # Return the platform data as confirmed by successful command execution
        return PlatformResponseDTO(
            message=f"Platform '{platform_data.service_name}' added successfully.",
            platform=PlatformDTO(
                service_name=platform_data.service_name,
                price_per_message=platform_data.price_per_message,
                fixed_price=platform_data.fixed_price
            )
        )
    except PlatformPriceAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except PriceNegativeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.critical(f"Unhandled exception adding platform price for user {current_user.uid}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

    # raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

