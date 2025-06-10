# src/features/bot/application/services/bot_access_service.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import List, Optional, Dict
from uuid import UUID

from src.features.bot.domain.entities.bot_entity import BotEntity
from src.features.bot.domain.repositories.bot_unit_of_work import BotUnitOfWork
from src.features.bot.exceptions.bot_exceptions import BotNotFoundError, BotAccessDeniedError





class BotAccessService:
    """
    Handles checking user access permissions for Bots.
    Uses repositories via the Unit of Work.
    """
    _uow: BotUnitOfWork

    def __init__(self, uow: BotUnitOfWork):
        self._uow = uow
        logger.debug("BotAccessService initialized.")

    async def check_single_bot_access(
            self,
            user_uid: UUID,
            bot_uid: UUID,
            allowed_roles: Optional[List[str]] = None
    ) -> BotEntity:
        """
        Centralized access control method.
        Ensures the user can access a specific bot, or raises a meaningful exception.
        Uses helper methods like `can_manage_bot`.
        """
        logger.debug(f"Checking access for user {user_uid} to bot {bot_uid}. Allowed roles: {allowed_roles}")

        async with self._uow:
            bot = await self._uow.bot_repository.find_by_uid(bot_uid)
            if not bot:
                logger.warning(f"Bot not found with UID: {bot_uid}")
                raise BotNotFoundError(f"Bot with UID {bot_uid} not found.")

            can_access = False

            if allowed_roles:
                can_access = await self.can_manage_bot(
                    user_uid=str(user_uid),
                    bot_uid=str(bot_uid),
                    allowed_roles=allowed_roles
                )
            else:
                # Fall back to: is owner or any participant
                can_access = str(bot.user_uid) == str(
                    user_uid) or await self._uow.bot_participant_repository.is_participant(
                    bot_uid=bot_uid,
                    user_uid=user_uid
                )

            if not can_access:
                logger.warning(f"Access denied: User {user_uid} does not have permission for bot {bot_uid}")
                raise BotAccessDeniedError(f"Access denied to the specified bot. Owner's uid: {bot.user_uid}")

        logger.debug(f"Access granted: User {user_uid} to bot {bot_uid}")
        return bot

    async def get_accessible_bots(
        self,
        user_uid: UUID,
        allowed_roles: Optional[List[str]] = None
    ) -> List[BotEntity]:
        """
        Gets a list of all bots accessible to the user (owned or participating with allowed roles).
        Uses existing repository methods.
        """
        accessible_bots_map: Dict[UUID, BotEntity] = {}

        async with self._uow:
            # 1. Get Owned Bots using the existing findall_by_user_uid method
            owned_bots = await self._uow.bot_repository.findall_by_user_uid(user_uid)
            for bot in owned_bots:
                accessible_bots_map[bot.uid] = bot

            # 2. Get Bots where user is a participant
            # get all bot participant entities for this user
            participant_entries = await self._uow.bot_participant_repository.find_bots_by_user_uid(user_uid)
            bots_to_fetch_uids = set()
            for p_entry in participant_entries:
                # Check role first before deciding to fetch the bot
                if allowed_roles is None or p_entry.role in allowed_roles:
                    # Add bot_uid to fetch list, only if not already owned
                    if p_entry.bot_uid not in accessible_bots_map:
                        bots_to_fetch_uids.add(p_entry.bot_uid)
                else:
                     logger.debug(f"Skipping participation in bot {p_entry.bot_uid} due to role '{p_entry.role}' not in {allowed_roles}")


            #   Fetch the actual BotEntities for the valid participant entries
            if bots_to_fetch_uids:
                uids_list = list(bots_to_fetch_uids)
                participant_bots_list = await self._uow.bot_repository.find_by_uids(uids_list)

                # Add the fetched bots to the map
                for bot in participant_bots_list:
                    if bot.uid in bots_to_fetch_uids:
                        accessible_bots_map[bot.uid] = bot
                    else:
                         logger.warning(f"find_by_uids returned bot {bot.uid} which was not in the requested list {uids_list}")

        # Convert map values back to a list
        all_accessible_bots = list(accessible_bots_map.values())
        logger.info(f"Total accessible bots found for user {user_uid}: {len(all_accessible_bots)}")
        return all_accessible_bots




    async def can_manage_bot(self, user_uid: str, bot_uid: str, allowed_roles: List[str] = None) -> bool:
        """
        Check if user can manage a bot (update, delete, etc).
        Returns True if user is owner or has one of the allowed roles.
        """
        async with self._uow:
            bot = await self._uow.bot_repository.find_by_uid(UUID(bot_uid))
            if not bot:
                return False

            # Owner always has access
            if str(bot.user_uid) == user_uid:
                return True

            # Check participant roles
            if allowed_roles:
                participant_role = await self._uow.bot_participant_repository.find_participant_role(
                    bot_uid=UUID(bot_uid),
                    user_uid=UUID(user_uid)
                )
                return participant_role in allowed_roles if participant_role else False

            return False

