# src/features/announcements/container.py

from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
# Adjust imports as per your project's structure
from src.core.mediator.mediator import Mediator
from src.features.support.application.commands.create_support.create_support_command_handler import \
    CreateSupportCommandHandler
from src.features.support.application.event_handlers.support_uploaded_event_handler import SupportUploadedEventHandler
from src.features.support.application.queries.get_supports.get_supports_query_handler import \
    GetSupportRequestsQueryHandler
from src.features.support.domain.uow.support_unit_of_work import SupportUnitOfWork
from src.features.support.infra.persistence.repositories.sqlalchemy_support_repository import \
    SQLAlchemySupportRepository
from src.features.support.infra.persistence.uow.sqlalchemy_support_unit_of_work import SQLAlchemySupportUnitOfWork
from src.infra.persistence.connection.sqlalchemy_engine import AsyncSessionLocal
from src.infra.services.s3.event_handlers.support_requested_event_handler import SupportRequestedEventHandler


# You might want a Query Handler too
# from src.features.announcements.application.queries.get_announcements.get_announcements_query_handler import GetAnnouncementsQueryHandler
# from src.features.announcements.application.queries.get_announcements.get_announcements_query import GetAnnouncementsQuery


class SupportContainer(containers.DeclarativeContainer):
    """
    Dependency Injection Container for the Announcements Bounded Context.
    """
    # Dependencies from parent container (e.g., ApplicationContainer)
    mediator = providers.Dependency(instance_of=Mediator)
    config = providers.DelegatedSingleton(Settings)
    user_lookup_service = providers.Dependency()

    # Database Session - Assumes a new session per request/operation for UoW
    # IMPORTANT: If you need a single session across multiple UoWs in one request,
    # you'd need a request-scoped provider here or manage it via FastAPI Dependencies.
    db_session: providers.Factory[AsyncSession] = providers.Factory(AsyncSessionLocal)

    @staticmethod
    def create_uow(session: AsyncSession) -> SupportUnitOfWork:
        """Only static method needed - creates UoW with repository"""
        support_repo=SQLAlchemySupportRepository(session=session)
        support_uow = SQLAlchemySupportUnitOfWork(session=session,support_repository=support_repo)
        return support_uow

    support_unit_of_work = providers.Factory(
        create_uow,
        session=db_session,
    )

    # Command Handlers
    create_support_command_handler = providers.Factory(
        CreateSupportCommandHandler,
        _user_lookup_service=user_lookup_service,
        _mediator=mediator
    )

    get_supports_query_handler = providers.Factory(
        GetSupportRequestsQueryHandler,
        _unit_of_work=support_unit_of_work,
        _mediator=mediator
    )

    # Event Handlers

    support_uploaded_event_handler = providers.Factory(
        SupportUploadedEventHandler,
        _unit_of_work=support_unit_of_work,
        _mediator=mediator
    )

