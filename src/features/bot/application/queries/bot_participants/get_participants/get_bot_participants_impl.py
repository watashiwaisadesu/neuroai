from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass, field # Import 'field' for mapper injection
from typing import List, Dict

from src.core.mediator.mediator import Mediator
from src.core.mediator.query import BaseQueryHandler
# Import the new GetParticipantsDTO and BotParticipantDTO
from src.features.bot.api.v1.dtos.get_participants_dto import GetParticipantsDTO
from src.features.bot.api.v1.dtos.bot_participant import BotParticipantDTO # Assuming this is the source of BotParticipantDTO
from src.features.bot.application.mappers.bot_participant_dto_mapper import BotParticipantDTOMapper # Import your mapper
from src.features.bot.application.queries.bot_participants.get_participants.get_bot_participants_query import GetBotParticipantsQuery
from src.features.bot.application.services.bot_access_service import BotAccessService
from src.features.bot.application.services.user_lookup_service import UserLookupService, UserInfo
from src.features.bot.domain.entities.bot_participant_entity import BotParticipantEntity # For mapper init
from src.features.bot.domain.repositories.bot_unit_of_work import BotUnitOfWork



@dataclass
class GetBotParticipantsQueryHandler(BaseQueryHandler[GetBotParticipantsQuery, GetParticipantsDTO]): # <-- Changed return type
    """Handler for retrieving participants of a bot."""

    _bot_uow: BotUnitOfWork
    _user_lookup_service: UserLookupService
    _access_service: BotAccessService
    _mediator: Mediator
    _allowed_roles: list[str]
    _bot_participant_mapper: BotParticipantDTOMapper = field(init=False, repr=False) # Inject the mapper

    def __post_init__(self):
        # Initialize the mapper
        self._bot_participant_mapper = BotParticipantDTOMapper(BotParticipantEntity, BotParticipantDTO)


    async def __call__(self, query: GetBotParticipantsQuery) -> GetParticipantsDTO: # <-- Changed return type
        """
        Handles retrieving participants:
        1. Validates access permissions for the current user to view the bot.
        2. Fetches the bot.
        3. Fetches participant entities for the target bot.
        4. Fetches corresponding user details (email, avatar).
        5. Maps the combined data to BotParticipantDTOs and wraps them in GetParticipantsDTO.
        """
        logger.info(f"User {query.current_user_uid} attempting to fetch participants for bot UID: {query.bot_uid}")

        # 1. Validate access permissions and fetch the target bot
        target_bot = await self._access_service.check_single_bot_access(
            user_uid=query.current_user_uid,
            bot_uid=query.bot_uid,
            allowed_roles=self._allowed_roles,
        )

        async with self._bot_uow as uow: # Use UoW context for bot operations

            # 2. Fetch participant entities for the target bot
            participant_entities = await uow.bot_participant_repository.find_by_bot_uid(target_bot.uid)
            logger.debug(f"Found {len(participant_entities)} participant entries for bot {target_bot.uid}.")

        mapped_participants: List[BotParticipantDTO] = []
        if not participant_entities:
            message = f"No participants found for bot {target_bot.uid}."
            logger.info(message)
            return GetParticipantsDTO(message=message, participants=[])

        # Extract unique user UIDs to fetch their details efficiently
        participant_user_uids = [
            str(participant.user_uid)
            for participant in participant_entities
            if participant.user_uid
        ]

        # 3. Fetch corresponding user details (email, avatar)
        user_details_list = await self._user_lookup_service.get_users_by_uids(participant_user_uids)
        user_details_map: Dict[str, UserInfo] = {
            str(user.uid): user for user in user_details_list if user and user.uid
        }
        logger.debug(f"Fetched details for {len(user_details_map)} participant users.")

        # 4. Map the combined data to BotParticipantDTOs
        for p_entity in participant_entities:
            if p_entity.user_uid is None:
                logger.warning(f"Participant entity {p_entity.uid} has a null user_uid. Skipping.")
                continue

            user_detail = user_details_map.get(str(p_entity.user_uid))

            try:
                # Use the injected mapper to create BotParticipantDTO, enriching with user_detail
                participant_dto = self._bot_participant_mapper.to_dto(p_entity, user_detail)
                mapped_participants.append(participant_dto)
            except Exception as e:
                logger.error(
                    f"Failed to map participant entity {p_entity.uid} to DTO for bot {target_bot.uid}: {e}",
                    exc_info=True
                )
                # Decide on error handling: skip, or include partial DTO, or raise
                # For now, we skip on mapping failure.

        message = f"Successfully fetched {len(mapped_participants)} participant(s) for bot {target_bot.uid}."
        logger.info(message)

        return GetParticipantsDTO(
            message=message,
            participants=mapped_participants
        )