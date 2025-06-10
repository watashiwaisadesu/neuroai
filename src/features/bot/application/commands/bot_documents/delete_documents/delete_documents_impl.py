from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass
from uuid import UUID
from typing import List

from src.core.base.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.features.bot.api.v1.dtos.delete_documents_dto import DeleteBotDocumentsResponseDTO
from src.features.bot.application.commands.bot_documents.delete_documents.delete_documents_command import DeleteBotDocumentsCommand

from src.features.bot.domain.repositories.bot_unit_of_work import BotUnitOfWork
from src.features.bot.application.services.bot_access_service import BotAccessService



@dataclass
class DeleteBotDocumentsCommandHandler(BaseCommandHandler[DeleteBotDocumentsCommand, DeleteBotDocumentsResponseDTO]):
    _unit_of_work: BotUnitOfWork
    _access_service: BotAccessService
    _mediator: Mediator
    _allowed_roles: list[str]

    async def __call__(self, command: DeleteBotDocumentsCommand) -> DeleteBotDocumentsResponseDTO:
        # Validate access first
        bot = await self._access_service.check_single_bot_access(
            user_uid=command.current_user_uid,
            bot_uid=command.bot_uid,
            allowed_roles=self._allowed_roles,
        )

        document_uids_to_delete: List[UUID] = command.document_uids_to_delete
        logger.info(f"Attempting to delete {len(document_uids_to_delete)} documents for bot {bot.uid}")

        deleted_uids: List[UUID] = []
        not_found_uids: List[UUID] = []

        try:
            async with self._unit_of_work:
                # 1. Verify documents belong to the bot
                found_documents = await self._unit_of_work.bot_document_repository.find_by_uids_and_bot_uid(
                    document_uids=document_uids_to_delete,
                    bot_uid=bot.uid
                )

                found_uids = {doc.uid for doc in found_documents}
                not_found_uids = [uid for uid in document_uids_to_delete if uid not in found_uids]

                if not found_documents:
                    logger.warning(f"No matching documents found for deletion for bot {bot.uid} with provided UIDs.")
                    return DeleteBotDocumentsResponseDTO(
                        message="No matching documents found to delete.",
                        not_found_document_uids=document_uids_to_delete
                    )

                # 2. Delete document records from the database
                uids_to_delete = [doc.uid for doc in found_documents]
                if uids_to_delete:
                    deleted_count = await self._unit_of_work.bot_document_repository.delete_by_uids(uids_to_delete)
                    deleted_uids = uids_to_delete
                    logger.info(f"Deleted {deleted_count} document records for bot {bot.uid}.")

        except Exception as e:
            logger.error(f"Error during document deletion for bot {bot.uid}: {e}", exc_info=True)
            raise

        message = f"{len(deleted_uids)} document(s) deleted successfully."
        if not_found_uids:
            message += f" {len(not_found_uids)} document(s) not found or not belonging to this bot."

        return DeleteBotDocumentsResponseDTO(
            message=message,
            deleted_document_uids=deleted_uids,
            not_found_document_uids=not_found_uids
        )
