from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import Dict, Optional

from src.features.bot.api.v1.dtos.get_documents_dto import BotDocumentResponseItemDTO
from src.features.bot.api.v1.dtos.get_user_bots_dto import BotDTO, BotServiceDTO, BotParticipantDTO
# Import the new BotDTOMapper
from src.features.bot.application.mappers.bot_dto_mapper import BotDTOMapper
from src.features.bot.application.services.user_lookup_service import UserLookupService, UserInfo
from src.features.bot.domain.entities.bot_entity import BotEntity
from src.features.bot.domain.repositories.bot_unit_of_work import BotUnitOfWork



# Initialize the BotDTOMapper once, as it's stateless
_bot_dto_mapper = BotDTOMapper(BotEntity, BotDTO)

# You might also want to define simple mappers for these nested DTOs if they become complex
# For now, inline list comprehensions are fine as they are simple one-to-one mappings.


async def build_bot_response(
        bot: BotEntity,
        bot_uow: BotUnitOfWork,
        user_lookup_service: UserLookupService
) -> Optional[BotDTO]:
    """
    Builds the complete BotDTO from a BotEntity and its related entities,
    using BotDTOMapper for core attributes and fetching nested data.
    """
    if not bot:
        logger.warning("build_bot_response received None bot entity, returning None.")
        return None

    try:
        # Use the mapper to get the core BotDTO attributes
        # This will already handle flattening AI settings and quota from the entity.
        bot_dto = _bot_dto_mapper.to_dto(bot)

        # --- Fetch and Map Related Services ---
        bot_service_entities = await bot_uow.bot_service_repository.find_by_bot_uid(bot.uid)
        bot_dto.bot_services = [
            BotServiceDTO(
                platform=s.platform,
                status=s.status,
                uid=s.uid,
                service_details=s.service_details # Ensure service_details is mapped correctly if it's a complex type
            )
            for s in bot_service_entities
        ]

        # --- Fetch and Map Participants ---
        participant_entities = await bot_uow.bot_participant_repository.find_by_bot_uid(bot.uid)

        if participant_entities:
            # Extract unique user UIDs to query user_lookup_service efficiently
            participant_user_uids = [
                str(p.user_uid)
                for p in participant_entities
                if p.user_uid
            ]

            # Get user details for participants
            user_details_list = await user_lookup_service.get_users_by_uids(participant_user_uids)
            user_details_map: Dict[str, UserInfo] = {
                str(user.uid): user for user in user_details_list
            }

            # Map participants to DTOs, enriching with user details
            for p_entity in participant_entities:
                user_detail = user_details_map.get(str(p_entity.user_uid))
                if user_detail:
                    bot_dto.participants.append(
                        BotParticipantDTO(
                            user_uid=p_entity.user_uid,
                            role=p_entity.role,
                            email=user_detail.email,
                            avatar=user_detail.avatar_file_url
                        )
                    )
                else:
                    logger.warning(f"User detail not found for participant user UID: {p_entity.user_uid} in bot {bot.uid}")

        # --- Fetch and Map Documents ---
        logger.debug(f"Fetching documents for bot UID: {bot.uid}")
        document_entities = await bot_uow.bot_document_repository.find_by_bot_uid(bot.uid)
        bot_dto.documents = [
            BotDocumentResponseItemDTO(
                document_uid=doc.uid,
                filename=doc.filename,
                content_type=doc.content_type
            )
            for doc in document_entities
        ]

        logger.debug(f"Successfully assembled full BotDTO for bot UID: {bot.uid} with {len(bot_dto.participants)} participants and {len(bot_dto.documents)} documents.")
        return bot_dto

    except Exception as e:
        logger.error(f"Error building complete BotDTO for bot UID {bot.uid}: {e}", exc_info=True)
        # Propagate the error or return None, depending on the error handling strategy
        return None