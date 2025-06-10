from abc import ABC, abstractmethod
from typing import List, Dict, Optional

# Import necessary domain objects if needed for input/output types
# (Using simple types for now)
# from src.features.bot.domain.value_objects.ai_configuration_vo import AIConfigurationSettings
# from src.features.bot.domain.value_objects.bot_quota_vo import BotQuota

class IGenerationService(ABC):
    """Interface for AI response generation service."""

    @abstractmethod
    async def generate_response(
        self,
        prompt_messages: List[Dict[str, str]], # e.g., [{"role": "user", "content": "Hi"}]
        system_prompt: Optional[str] = None,
        config: Optional[object] = None, # Placeholder for AIConfigurationSettings
        quota: Optional[object] = None, # Placeholder for BotQuota
        last_user_message: Optional[str] = None,
        # Add other necessary parameters like model_name, user_id etc.
    ) -> Optional[str]: # Returns the generated text content or None on failure
        """
        Generates a response based on the provided messages and configuration.
        Handles interaction with the specific AI model API.
        """
        raise NotImplementedError



