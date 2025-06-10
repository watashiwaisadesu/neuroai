from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import Optional, Type

from src.features.bot.api.v1.dtos.bot_dto import BotDTO
from src.features.bot.domain.entities.bot_entity import BotEntity



# --- Mapper for Full BotDTO ---
class BotDTOMapper:
    """
    Specific mapper between BotEntity and BotDTO,
    handling the flattening of AIConfigurationSettings and BotQuota value objects.
    This mapper is responsible for mapping the core attributes of the BotEntity.
    Nested lists (services, participants, documents) are expected to be populated
    separately in the utility function that orchestrates the DTO creation,
    as indicated by the empty list defaults.
    """

    def __init__(self, entity_cls: Type[BotEntity], dto_cls: Type[BotDTO]):
        """
        Initializes the mapper with the specific entity and DTO classes.
        """
        self.entity_cls = entity_cls
        self.dto_cls = dto_cls
        logger.debug(f"BotDTOMapper initialized for {entity_cls.__name__} and {dto_cls.__name__}")

    def to_dto(self, entity: BotEntity) -> Optional[BotDTO]:
        """
        Maps a BotEntity domain object to a BotDTO,
        extracting and flattening fields from the entity and its nested value objects.
        Handles potential None values by providing sensible defaults for the DTO.
        """
        if not entity:
            logger.debug("BotDTOMapper.to_dto received None entity, returning None.")
            return None

        logger.debug(f"Mapping BotEntity (UID: {entity.uid}) core attributes to BotDTO.")
        try:
            # Safely get AI settings and Quota, providing default empty objects if they could be None.
            # However, if your BotEntity's constructor ensures they are always instantiated (even with defaults),
            # these 'or' checks might be redundant. Assuming they *could* be None here.
            ai_settings = entity.ai_settings
            quota = entity.quota

            dto_data = {
                # BaseEntity fields (inherited by BotEntity)
                "uid": entity.uid,
                "created_at": entity.created_at,
                "updated_at": entity.updated_at,

                # Core Bot fields (access via properties for consistency)
                "user_uid": entity.user_uid,
                "bot_type": entity.bot_type,
                "name": entity.name if entity.name is not None else "",
                "status": entity.status if entity.status is not None else "",
                "tariff": entity.tariff if entity.tariff is not None else "",
                "crm_lead_id": entity.crm_lead_id,
                "auto_deduction": entity.auto_deduction,

                # AI Settings from AIConfigurationSettings Value Object.
                # Access attributes only if ai_settings object exists. Provide sensible defaults.
                "instructions": ai_settings.instructions if ai_settings and ai_settings.instructions is not None else "",
                "temperature": ai_settings.temperature if ai_settings and ai_settings.temperature is not None else 0.0,
                "max_response": ai_settings.max_response if ai_settings and ai_settings.max_response is not None else 0,
                "top_p": ai_settings.top_p if ai_settings and ai_settings.top_p is not None else 0.0,
                "top_k": ai_settings.top_k if ai_settings and ai_settings.top_k is not None else 0,
                "repetition_penalty": ai_settings.repetition_penalty if ai_settings and ai_settings.repetition_penalty is not None else 0.0,
                "generation_model": ai_settings.generation_model if ai_settings and ai_settings.generation_model is not None else "",

                # Quota Settings from BotQuota Value Object.
                # Access attributes only if quota object exists. Provide sensible defaults.
                "token_limit": quota.token_limit if quota and quota.token_limit is not None else 0,
                "tokens_left": quota.tokens_left if quota and quota.tokens_left is not None else 0,

                # Nested lists are expected to be populated separately by orchestration logic
                "bot_services": [],
                "participants": [],
                "documents": []
            }

            # Create DTO instance using the dynamically provided dto_cls
            bot_dto_instance = self.dto_cls(**dto_data)
            logger.debug(f"Successfully mapped core BotEntity attributes to BotDTO (UID: {entity.uid}).")
            return bot_dto_instance

        except Exception as e:
            logger.error(
                f"Error mapping BotEntity core attributes to BotDTO (UID: {entity.uid if entity else 'N/A'}): {e}",
                exc_info=True
            )
            # Re-raise the exception to indicate a critical mapping failure.
            raise