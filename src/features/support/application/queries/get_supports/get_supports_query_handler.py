# src/features/support/application/queries/get_support_requests/get_support_requests_query_handler.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass
from typing import List

from src.core.mediator.mediator import Mediator
from src.core.mediator.query import BaseQueryHandler  # Assuming BaseQueryHandler is defined
from src.features.support.api.v1.dtos.get_support_dto import SupportDTO
from src.features.support.application.queries.get_supports.get_supports_query import GetSupportsQuery
from src.features.support.domain.entities.support_entity import SupportEntity
from src.features.support.domain.uow.support_unit_of_work import SupportUnitOfWork




@dataclass
class GetSupportRequestsQueryHandler(BaseQueryHandler[GetSupportsQuery, List[SupportDTO]]):
    """
    Handles the GetSupportRequestsQuery by fetching support requests
    from the repository and mapping them to DTOs.
    """
    _unit_of_work: SupportUnitOfWork
    _mediator: Mediator

    async def __call__(self, query: GetSupportsQuery) -> List[SupportDTO]:
        logger.info(f"Fetching support requests for user {query.user_uid}, category: {query.category}")

        # Fetch entities from the repository
        # The repository method might be `find_by_user_uid_and_category` or similar
        async with self._unit_of_work as uow:
            # Pass the category filter to the repository method
            support_entities: List[SupportEntity] = await uow.support_repository.get_all_by_user_uid(
                user_uid=query.user_uid,
                category=query.category # This is correctly passed
            )

        # Map entities to DTOs
        # You might have a dedicated mapper class/function, or do it inline
        support_dtos: List[SupportDTO] = []
        for entity in support_entities:
            support_dtos.append(
                SupportDTO(
                    uid=entity.uid,
                    user_uid=entity.user_uid,
                    email=entity.email,
                    subject=entity.subject,
                    message=entity.message,
                    category=entity.category,
                    status=entity.status,
                    created_at=entity.created_at,
                    updated_at=entity.updated_at,
                    attachment_urls=[att.file_url for att in entity.attachments]
                )
            )
        logger.info(f"Found {len(support_dtos)} support requests for user {query.user_uid}.")
        return support_dtos
