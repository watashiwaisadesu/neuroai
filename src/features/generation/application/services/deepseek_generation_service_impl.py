# src/features/generation/application/services/deepseek_generation_service_impl.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
import aiohttp
from typing import List, Dict, Optional, Any

from src.features.generation.application.services.generation_service import IGenerationService
from src.features.bot.domain.value_objects.ai_configuration_vo import AIConfigurationSettings  # For config type hint
from src.features.bot.domain.value_objects.bot_quota_vo import BotQuota  # For quota type hint
from src.config import Settings



settings: Settings = Settings()

class DeepSeekGenerationServiceImpl(IGenerationService):
    """
    Implementation of IGenerationService that interacts with a DeepSeek-compatible API.
    """

    async def generate_response(
            self,
            prompt_messages: List[Dict[str, str]],  # Expects [{"role": "user/assistant/system", "content": "..."}]
            system_prompt: Optional[str] = None,
            config: Optional[AIConfigurationSettings] = None,  # Bot's AI settings
            quota: Optional[BotQuota] = None,  # Bot's quota
            last_user_message: Optional[str] = None  # Can be derived from prompt_messages
    ) -> Optional[str]:  # Returns the generated text content or None on failure
        """
        Generates a response using the DeepSeek API.
        """
        if not config:
            logger.warning("DeepSeek: AIConfigurationSettings (config) not provided. Using defaults.")
            # Create default if needed, or rely on API defaults
            # For now, we'll assume some defaults or that the API handles missing options.
            effective_config = AIConfigurationSettings()  # Default instance
        else:
            effective_config = config

        # --- 1. Prepare Messages ---
        formatted_messages = []
        if system_prompt:  # Use system_prompt from argument if provided
            formatted_messages.append({"role": "system", "content": system_prompt.strip()})
        elif effective_config.instructions:  # Fallback to instructions from config
            formatted_messages.append({"role": "system", "content": effective_config.instructions.strip()})

        # Add the rest of the message history
        formatted_messages.extend(prompt_messages)
        logger.debug(
            f"DeepSeek: Sending {len(formatted_messages)} messages. Last user message: '{formatted_messages[-1]['content'][:50]}...'")

        # --- 2. Prepare API Options ---
        # Use specific model from settings or fallback to a default
        model_name = getattr(effective_config, 'generation_model', settings.LLM_MODEL)
        if not model_name:  # Ensure there's a model to use
            logger.error("DeepSeek: No generation model specified in config or settings default.")
            return None

        api_options = {
            "num_predict": effective_config.max_response if effective_config.max_response is not None else 250,
            "temperature": effective_config.temperature if effective_config.temperature is not None else 0.7,
            "top_p": effective_config.top_p if effective_config.top_p is not None else 0.9,
            "top_k": effective_config.top_k if effective_config.top_k is not None else 40,
            "repeat_penalty": effective_config.repetition_penalty if effective_config.repetition_penalty is not None else 1.1,
            # Add other DeepSeek specific options if available in AIConfigurationSettings
        }
        logger.debug(f"DeepSeek: Using model '{model_name}' with options: {api_options}")

        # --- 3. Make API Call ---
        payload = {
            "model": model_name,
            "messages": formatted_messages,
            "stream": False,  # For non-streaming version
            "key": settings.LLM_API_KEY,  # Key from settings
            "options": api_options
        }

        try:
            async with aiohttp.ClientSession() as http_session:
                logger.info(f"DeepSeek: Posting to {settings.LLM_API_URL}")
                async with http_session.post(
                        settings.LLM_API_URL,
                        headers={"Content-Type": "application/json"},
                        json=payload
                ) as resp:
                    logger.debug(f"DeepSeek: Received status {resp.status}")
                    if resp.status != 200:
                        error_content = await resp.text()
                        logger.error(f"DeepSeek API call failed with status {resp.status}: {error_content}")
                        # In a real app, raise a specific exception
                        # raise AssistantProcessingError(f"DeepSeek API call failed with status {resp.status}")
                        return None  # Or raise an exception

                    response_data = await resp.json()
                    assistant_text = response_data.get("message", {}).get("content", "").strip()
                    prompt_tokens: int = response_data.get("prompt_eval_count", 0)
                    completion_tokens: int = response_data.get("eval_count", 0)
                    total_used: int = prompt_tokens + completion_tokens
                    logger.info(
                        f"DeepSeek: Response received. Tokens used: {total_used} (P:{prompt_tokens}, C:{completion_tokens})")

                    # --- 4. Update Quota (if provided and mutable) ---
                    if quota and hasattr(quota, 'deduct') and callable(quota.deduct):
                        try:
                            quota.deduct(amount=total_used)
                            logger.info(
                                f"DeepSeek: Deducted {total_used} tokens from quota. Remaining: {quota.tokens_left}")
                        except ValueError as e:
                            logger.warning(f"DeepSeek: Failed to deduct tokens from quota: {e}")
                        except Exception as e:
                            logger.error(f"DeepSeek: Unexpected error deducting tokens: {e}", exc_info=True)
                    elif quota:
                        logger.warning(
                            "DeepSeek: Quota object provided but 'deduct' method is missing or not callable.")

                    return assistant_text

        except aiohttp.ClientError as e:
            logger.error(f"DeepSeek: aiohttp.ClientError during API call: {e}", exc_info=True)
            # raise AssistantProcessingError(f"Network error connecting to DeepSeek: {e}")
            return None
        except Exception as e:
            logger.error(f"DeepSeek: Unexpected error in generate_response: {e}", exc_info=True)
            # raise AssistantProcessingError(f"Unexpected error during AI generation: {e}")
            return None


import asyncio  # Add for stream stub

