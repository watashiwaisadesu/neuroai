# src/infra/logging/custom_sqlalchemy_handler.py

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, Union

from aiologger.formatters.base import Formatter  # Aiologger's base formatter
from aiologger.handlers.base import Handler  # Base handler from aiologger
from aiologger.levels import LogLevel
from aiologger.records import LogRecord

# Assuming your async session maker is here
from src.infra.persistence.connection.sqlalchemy_engine import AsyncSessionLocal
# Assuming your ORM model for logs is here
from src.infra.persistence.models.log_orm import LogEntryORM


# Assuming your async engine is here (passed to handler)

class CustomSQLAlchemyHandler(Handler):
    """
    A custom asynchronous logging handler that writes log records to a database
    using SQLAlchemy's asyncio capabilities.

    This implementation uses AsyncSessionLocal to get a new session for each log entry,
    ensuring non-blocking and isolated database writes.
    """

    def __init__(
        self,
        level: Union[str, int, LogLevel] = LogLevel.NOTSET,
        formatter: Optional[Formatter] = None,
        # We need the async session maker to create sessions for logging
        async_session_maker=AsyncSessionLocal, # Use the imported AsyncSessionLocal as default
        # No need to explicitly pass engine if session_maker is already bound to it,
        # but could be useful if you wanted to pass a different engine for logging.
        # engine: AsyncEngine = global_async_engine # Example if passing engine separately
    ) -> None:
        super().__init__(level=level)
        self.async_session_maker = async_session_maker
        if formatter is None:
            self.formatter = Formatter(fmt='%(message)s')  # Only the message content
        else:
            self.formatter = formatter

        self._initialization_lock = asyncio.Lock() # For potential future persistent connection needs
        self._initialized = False # Tracks if any setup (like connection check) has run

    @property
    def initialized(self) -> bool:
        """Indicates if the handler is ready to emit logs."""
        return self._initialized

    async def emit(self, record: LogRecord) -> None:
        """
        Asynchronously writes the log record to the database.
        """
        if not self.filter(record): # Apply filters first
            return

        # Acquire a new asynchronous session for this log entry
        async with self.async_session_maker() as session:
            try:
                formatted_message = self.formatter.format(record)
                log_entry = LogEntryORM(
                    log_level=record.levelname,
                    source=record.name or record.module,
                    message=formatted_message,
                    timestamp=datetime.fromtimestamp(record.created, tz=timezone.utc)
                )

                session.add(log_entry)

                # YOU MUST UNCOMMENT THIS LINE TO SAVE THE LOG
                await session.commit()

            except Exception as exc:
                await session.rollback()
                # Handle the error, typically by logging to stderr or another fallback handler
                await self.handle_error(record, exc)

    async def flush(self) -> None:
        """
        No explicit flush needed for per-request session model.
        """
        pass # The commit takes care of flushing

    async def close(self) -> None:
        """
        Clean up resources.
        """
        # For a per-session handler, there's no long-lived connection to close here.
        # The sessions are closed automatically by the 'async with' block.
        # If there were a persistent connection pool managed by the handler, it would be closed here.
        self._initialized = False # Reset state
        # Remove the handler from the root logger's list if it's still there
        if self in logging.getLogger().handlers:
            logging.getLogger().removeHandler(self)

