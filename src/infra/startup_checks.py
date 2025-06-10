import asyncio
import logging # Using standard logging for these checks, can be replaced by async_logger later if preferred

from src.infra.services.redis.redis_client import redis_client
from src.infra.services.redis.exceptions import RedisConnectionError
from src.infra.services.celery.app import celery
from src.infra.services.celery.exceptions import CeleryConnectionError
from celery.exceptions import TimeoutError as CeleryTimeoutError

# Get a logger for this module
local_logger = logging.getLogger(__name__)


async def check_redis_connection():
    """Checks the connection to the Redis server."""
    local_logger.info("Checking Redis connection...")
    try:
        await redis_client.ping()
        local_logger.info("✅ Redis is up and running.")
    except ConnectionError as e:
        local_logger.error(f"❌ Redis connection failed: {e}", exc_info=True)
        raise RedisConnectionError("Redis connection failed.") from e
    except Exception as e:
        local_logger.error(f"❌ An unexpected error occurred during Redis check: {e}", exc_info=True)
        raise RedisConnectionError(f"Unexpected error during Redis check: {e}") from e


async def check_celery_connection():
    """Checks if at least one Celery worker is online and connected."""
    local_logger.info("Checking Celery connection...")
    try:
        # Use celery.control.ping() to check for active workers.
        # This method is synchronous, so run it in a separate thread using asyncio.to_thread.
        # The timeout ensures we don't wait indefinitely if no workers respond.
        # It returns a list of dictionaries, one for each worker that responded.
        replies = await asyncio.to_thread(celery.control.ping, timeout=2) # 2-second timeout

        if replies:
            local_logger.info(f"✅ Celery worker(s) online: {len(replies)} worker(s) responded.")
        else:
            # If replies is empty, no workers responded within the timeout
            local_logger.warning("❌ No Celery workers responded to ping within timeout. Workers might be offline or broker is unreachable.")
            raise CeleryConnectionError("No Celery workers online within timeout.")
    except CeleryTimeoutError as e:
        # This specific exception occurs if the ping operation itself times out
        local_logger.error(f"❌ Celery worker ping timed out: {e}", exc_info=True)
        raise CeleryConnectionError("Celery worker ping timed out.") from e
    except Exception as e:
        # Catch any other general exceptions during the worker check
        local_logger.error(f"❌ Celery worker check failed: {e}", exc_info=True)
        raise CeleryConnectionError(f"Celery worker check failed: {e}") from e

