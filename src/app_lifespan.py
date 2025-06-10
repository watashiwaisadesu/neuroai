from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.di_container import ApplicationContainer, initialize_identity_container, initialize_notification_container, \
    initialize_application_container, initialize_bot_container, initialize_telegram_container, \
    initialize_conversation_container, initialize_announcement_container, initialize_support_container, \
    initialize_platform_price_container
from src.app_wiring import get_modules_to_wire
from src.infra.persistence.models.models_loader import import_all_orm_models # NEW import
from src.infra.startup_checks import check_redis_connection, check_celery_connection # NEW import

# Using standard logging for initial messages if async_logger isn't fully configured yet
# The specific logger for this module.
from src.infra.logging.setup_async_logging import setup_async_logging, async_logger

logger = async_logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for FastAPI application startup and shutdown events.
    Handles middleware registration, dependency injection wiring,
    ORM model loading, and external service checks.
    """
    logger.info("FastAPI application lifespan: Startup initiated.")

    app_container = ApplicationContainer()
    modules_to_wire = get_modules_to_wire() # Get modules from app_wiring.py
    app_container.wire(modules=modules_to_wire)
    logger.info("Dependency injection container wired.")

    # 3. Initialize specific feature containers
    await initialize_application_container(app_container)
    await initialize_identity_container(app_container)
    await initialize_notification_container(app_container)
    await initialize_bot_container(app_container)
    await initialize_conversation_container(app_container)
    await initialize_telegram_container(app_container)
    await initialize_announcement_container(app_container)
    await initialize_support_container(app_container)
    await initialize_platform_price_container(app_container)
    logger.info("Application containers initialized.")


    # 5. Perform external service health checks
    try:
        await check_redis_connection()
        await check_celery_connection()
        logger.info("All external service connections checked successfully.")
    except Exception as e:
        logger.critical(f"Critical external service connection failed during startup: {e}", exc_info=True)
        # Depending on your desired behavior, you might want to raise the exception
        # to prevent the app from starting if these services are critical.
        raise # Re-raise to prevent app from starting without critical services

    # This log should now go into the database if async_logger is fully set up
    # using the setup_async_logging from src.infra.logging.setup_async_logging.
    # Note: If async_logger is not yet fully configured to write to DB at this point,
    # these logs might still go to console/default handler.
    # The initial setup_async_logging call must happen *before* this lifespan.
    # For logs within lifespan, ensure async_logger is globally accessible and configured.
    # We will ensure this is done in main.py before the FastAPI app is created.
    if async_logger:
        async_logger.info("FastAPI application startup completed, async_logger now active for application logs.")
        # async_logger.error("Test error log after DB setup - should be in DB via async_logger!") # Your test log
    else:
        logger.info("FastAPI application startup completed. async_logger not fully ready for lifespan logs.")


    yield # Application runs here

    # Shutdown events can be added here if needed
    logger.info("FastAPI application lifespan: Shutdown initiated.")

