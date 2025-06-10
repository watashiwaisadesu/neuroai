from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
import uuid
from dataclasses import dataclass

from src.core.base.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.features.bot.api.v1.dtos.upload_documents_dto import UploadBotDocumentsResponseDTO, UploadedDocumentInfoDTO
from src.features.bot.application.commands.bot_documents.upload_documents.upload_documents_command import \
    UploadBotDocumentsCommand
from src.features.bot.application.services.bot_access_service import BotAccessService
from src.features.bot.domain.entities.bot_document_entity import BotDocumentEntity
from src.features.bot.domain.repositories.bot_unit_of_work import BotUnitOfWork
from src.features.bot.exceptions.bot_exceptions import DocumentUploadFailedError




@dataclass
class UploadBotDocumentsCommandHandler(BaseCommandHandler[UploadBotDocumentsCommand, UploadBotDocumentsResponseDTO]):
    _unit_of_work: BotUnitOfWork
    _access_service: BotAccessService
    _mediator: Mediator
    _allowed_roles: list[str]

    async def __call__(self, command: UploadBotDocumentsCommand) -> UploadBotDocumentsResponseDTO:
        logger.info(f"User {command.current_user_uid} uploading documents to bot {command.bot_uid}")

        # Step 1: Validate access
        bot = await self._access_service.check_single_bot_access(
            user_uid=command.current_user_uid,
            bot_uid=command.bot_uid,
            allowed_roles=self._allowed_roles,
        )

        documents = []
        for file in command.files:
            try:
                if not file.filename:
                    continue
                content = await file.read()
                await file.close()

                documents.append(BotDocumentEntity(
                    uid=uuid.uuid4(),
                    bot_uid=bot.uid,
                    filename=file.filename,
                    content_type=file.content_type,
                    file_data=content
                ))
            except Exception as e:
                logger.error(f"Failed to process file {file.filename}: {e}", exc_info=True)

        if not documents:
            raise DocumentUploadFailedError("No valid documents to upload.")

        async with self._unit_of_work:
            saved_docs = await self._unit_of_work.bot_document_repository.create_many(documents)

        return UploadBotDocumentsResponseDTO(
            message=f"{len(saved_docs)} documents uploaded successfully to bot {bot.uid}.",
            documents=[
                UploadedDocumentInfoDTO(document_uid=doc.uid, filename=doc.filename)
                for doc in saved_docs
            ]
        )
