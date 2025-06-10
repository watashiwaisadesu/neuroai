import logging
import sys

# Import core configuration and logging setup
from src.config import Settings
from src.infra.logging.setup_async_logging import setup_async_logging, async_logger

# Import the new modular components
from src.app_lifespan import lifespan
from src.api.main_router import main_api_router
from src.exception_handlers import app_exception_handler, custom_validation_exception_handler
from src.core.base.exception import AppException
from src.infra.persistence.models.models_loader import import_all_orm_models
from src.middleware import register_middleware # NEW IMPORT

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError


# 1. Load Settings
_settings = Settings()

# 2. Import all ORM models
# This must happen before logging setup if the logging handler uses ORM models
# and before the FastAPI app is created, to ensure all mappings are in place.
import_all_orm_models()
# Use standard logging for this initial message, as async_logger might not be fully configured yet
logging.getLogger(__name__).info("All ORM models imported successfully before logging and app setup.")


# 3. Configure Async Logging
# This must be done BEFORE creating the FastAPI app and using the logger.
setup_async_logging(
    external_library_level_log=_settings.EXTERNAL_LIBRARY_LEVEL_LOG,
    log_level=_settings.LOG_LEVEL
)
logger = async_logger # Assign the configured async_logger
logger.info("Initial logging setup complete and async_logger configured.")


# 4. Register Middleware
# Middleware must be added BEFORE the FastAPI application instance is created.
app = FastAPI(title="NeEro-WoRkErs") # Create app instance first
register_middleware(app) # Register middleware here
logger.info("Middleware registered to FastAPI app.")


# 5. Assign Lifespan to the app instance
app.add_event_handler("startup", lifespan(app).__aenter__)
app.add_event_handler("shutdown", lifespan(app).__aexit__)


# 6. Register Custom Exception Handlers
app.exception_handler(AppException)(app_exception_handler)
app.exception_handler(RequestValidationError)(custom_validation_exception_handler)
logger.info("Custom exception handlers registered.")

# 7. Include Main API Router
app.include_router(main_api_router)
logger.info("Main API router included.")


# Optional: Add a simple root endpoint for basic health check or info
@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI application!"}

