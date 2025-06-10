import sys
from src.infra.logging.setup_async_logging import async_logger

# Get a logger for this module
# We're using the standard logging here, but you can switch to async_logger if it's available
# and configured at this stage of startup.
# For simplicity, we'll assume standard logging or a basic setup from your main logging config.
logger = async_logger

def import_all_orm_models():
    """
    Imports all ORM model modules to ensure they are registered with SQLAlchemy's metadata.
    This function should be called early in the application's lifespan.
    """
    logger.info("Importing ORM modules...")
    try:
        # --- Identity ---
        from src.features.identity.infra.persistence.models import user
        # --- Bot ---
        from src.features.bot.infra.persistence.models import bot
        from src.features.bot.infra.persistence.models import bot_service
        from src.features.bot.infra.persistence.models import bot_participant
        from src.features.support.infra.persistence.models import support_orm
        from src.features.support.infra.persistence.models import support_attachment_orm
        # --- Payments ---
        from src.features.payments.infra.persistence.models import payment
        # Add imports for any other ORM model modules you have...
        # Example: from src.features.your_feature.infra.persistence.models import your_model
        logger.info("ORM modules imported successfully.")
    except ImportError as e:
        logger.error(f"Error importing ORM modules: {e}", exc_info=True)
        # It's critical to ensure ORM models are loaded for the app to function.
        # Consider re-raising or exiting based on your application's error handling strategy.
        sys.exit(1) # Exit if critical ORM modules cannot be imported

