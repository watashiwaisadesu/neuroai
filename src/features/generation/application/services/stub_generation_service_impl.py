
# src/features/generation/application/services/stub_generation_service_impl.py (New file)

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import List, Dict, Optional

# Import the interface
from src.features.generation.application.services.generation_service import IGenerationService



class StubGenerationServiceImpl(IGenerationService):
    """
    A simple stub implementation of the generation service.
    Returns a fixed response for testing/development purposes.
    """

    async def generate_response(
        self,
        prompt_messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        config: Optional[object] = None, # Ignored by stub
        quota: Optional[object] = None, # Ignored by stub
        last_user_message: Optional[str] = None
    ) -> Optional[str]:
        """Returns a predefined stub response."""
        logger.info(f"StubGenerationServiceImpl called. Input messages count: {len(prompt_messages)}")
        logger.debug(f"StubGenerationServiceImpl - System Prompt: {system_prompt}")
        logger.debug(f"StubGenerationServiceImpl - Config: {config}")
        logger.debug(f"StubGenerationServiceImpl - Quota: {quota}")
        logger.debug(f"StubGenerationServiceImpl - Last User Message: {prompt_messages[-1]['content'] if prompt_messages else 'N/A'}")

        stub_response = f"This is a stub response to: '{last_user_message}'"

        logger.info(f"StubGenerationServiceImpl returning: '{stub_response}'")

        # Here you could also simulate token deduction if the quota object was mutable
        # if quota and hasattr(quota, 'deduct'):
        #     try:
        #         quota.deduct(5) # Simulate deducting 5 tokens
        #         logger.debug("Stub simulated token deduction.")
        #     except Exception as e:
        #          logger.warning(f"Stub failed to simulate token deduction: {e}")

        return stub_response