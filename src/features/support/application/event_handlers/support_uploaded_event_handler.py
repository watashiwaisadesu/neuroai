
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass

from src.core.base.event import BaseEventHandler
from src.core.mediator.mediator import Mediator
from src.features.support.domain.entities.support_entity import SupportEntity  # Renamed import
from src.features.support.domain.events.support_uploaded_event import SupportUploadedEvent  # Renamed import
from src.features.support.domain.uow.support_unit_of_work import SupportUnitOfWork




@dataclass(kw_only=True)
class SupportUploadedEventHandler(BaseEventHandler[SupportUploadedEvent, None]): # Renamed class
    """
    Application handler that creates the support entity in the database
    after its attachments have been successfully uploaded.
    """
    _unit_of_work: SupportUnitOfWork
    _mediator: Mediator

    async def handle(self, event: SupportUploadedEvent) -> None:
        logger.info(f"Creating support item in database for item_id: {event.uid}") # Updated log message, item_id
        try:
            # We now need to create SupportAttachmentEntity objects from the URLs
            # and pass them to the SupportEntity.create method.
            from src.features.support.domain.entities.support_attachment_entity import SupportAttachmentEntity

            attachment_entities = []
            for att_data in event.attachments_data:  # Iterate over the rich attachment data
                # Create SupportAttachmentEntity for each uploaded item
                attachment_entity = SupportAttachmentEntity.create(
                    support_uid=event.uid,  # Link to the main support request
                    file_url=att_data["file_url"],
                    file_name=att_data["file_name"],
                    content_type=att_data["content_type"],
                    file_size=att_data["file_size"]
                )
                attachment_entities.append(attachment_entity)

            async with self._unit_of_work as uow:
                support_item = SupportEntity.create( # Renamed variable
                    uid=event.uid,
                    user_uid=event.user_uid,
                    email=event.email,
                    subject=event.subject,
                    message=event.message,
                    category=event.category,
                    attachments=attachment_entities,
                )
                await uow.support_repository.create(support_item) # Renamed method if needed

                logger.info(f"Successfully created support item {support_item.uid} for item_id: {event.uid}") # Updated log message

        except Exception as e:
            logger.error(
                f"Failed to create support entity for item_id {event.uid} after upload: {e}", # Updated log message
                exc_info=True
            )
            raise