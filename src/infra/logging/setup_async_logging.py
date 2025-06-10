# src/infra/logging/setup_async_logging.py

import logging
# Import the custom handler
from src.infra.logging.custom_sqlalchemy_handler import CustomSQLAlchemyHandler

# Import aiologger's Logger class
from aiologger.logger import Logger
from aiologger.levels import LogLevel

# This will be your application's primary logger instance
# It's important to initialize it globally or pass it around
# Here, we'll configure the root logger to be an aiologger.logger.Logger instance
# This is a common pattern, but be mindful of any other places that might
# implicitly get the standard logging.getLogger() without configuration.
async_logger = Logger(name='', level=LogLevel.NOTSET)


def setup_async_logging(external_library_level_log: str, log_level: str):
    """
    Sets up the asynchronous database logging handler using your CustomSQLAlchemyHandler,
    and configures aiologger's Logger instance.
    Args:
        external_library_level_log: Log level for external libraries (e.g., 'WARNING').
        log_level: Global log level for internal application logs (e.g., 'INFO').
    """
    # Instantiate your custom handler
    db_handler = CustomSQLAlchemyHandler(
        level=logging.getLevelName(log_level), # Set the minimum level for this handler
    )

    # Add the handler to the aiologger instance
    # Ensure it's added only once to prevent duplicate log entries
    if not any(isinstance(h, CustomSQLAlchemyHandler) for h in async_logger.handlers):
        async_logger.add_handler(db_handler)

    # Set the global logging level for the aiologger instance
    # Set the global logging level for the aiologger instance.
    # This is important as handlers only process logs that pass this global level.
    current_level = async_logger.level
    target_level_int = logging.getLevelName(log_level)
    if current_level == LogLevel.NOTSET or current_level > target_level_int:
        # CRITICAL FIX: Assign directly to the 'level' property, do NOT use setLevel()
        async_logger.level = target_level_int

    async_logger.info("FastAPI: Custom Async Database Logging Handler Prepared.")


    # Optional: If you still want console output from aiologger's logger,
    # you might add an AsyncStreamHandler.
    # from aiologger.handlers.streams import AsyncStreamHandler
    # stream_handler = AsyncStreamHandler(level=logging.INFO)
    # stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    # if not any(isinstance(h, AsyncStreamHandler) for h in async_logger.handlers):
    #     async_logger.addHandler(stream_handler)


    # It's generally good practice to remove default StreamHandlers from the root logger
    # if you're taking full control with aiologger.
    # However, for external libraries that might log to the standard root logger,
    # you might keep a standard StreamHandler or configure aiologger to propagate.
    # For now, let's just make sure aiologger is the primary.
    # logging.getLogger().propagate = False # Disable propagation to root logger if you want full aiologger control

    async_logger.info("FastAPI: Custom Async Database Logging Handler Prepared.")
