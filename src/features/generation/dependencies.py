
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from fastapi import Depends

from src.features.generation.application.services.deepseek_generation_service_impl import DeepSeekGenerationServiceImpl
# Import interface and stub implementation
from src.features.generation.application.services.generation_service import IGenerationService
from src.features.generation.application.services.stub_generation_service_impl import StubGenerationServiceImpl





# --- Generation Service Provider ---
def get_stub_generation_service() -> IGenerationService: # Return the interface type
    """Provides an instance of the StubGenerationServiceImpl."""
    logger.debug("Providing StubGenerationServiceImpl")
    return StubGenerationServiceImpl()

def get_deepseek_generation_service() -> IGenerationService: # Return the interface type
    """Provides an instance of the StubGenerationServiceImpl."""
    logger.debug("Providing StubGenerationServiceImpl")
    return DeepSeekGenerationServiceImpl()