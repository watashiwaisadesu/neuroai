# src/features/announcements/container.py

from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
# Adjust imports as per your project's structure
from src.core.mediator.mediator import Mediator
from src.features.announcement.application.queries.get_all_announcements.get_all_announcements_query_handler import \
    GetAllAnnouncementsQueryHandler

from src.features.announcement.domain.repositories.announcement_repository import AnnouncementRepository
from src.features.announcement.domain.uow.announcement_unit_of_work import AnnouncementUnitOfWork
from src.features.announcement.infra.persistence.repositories.announcement_repository_handler import \
    AnnouncementRepositoryHandler
from src.features.announcement.infra.persistence.uow.announcement_unit_of_work_handler import \
    AnnouncementUnitOfWorkHandler

from src.features.announcement.application.commands.create_announcement.create_announcement_command_handler import \
    CreateAnnouncementCommandHandler
from src.features.prices.application.commands.create_platform_price_command_handler import \
    CreatePlatformPriceCommandHandler
from src.features.prices.application.queries.get_platform_prices_query_handler import GetPlatformPricesQueryHandler
from src.features.prices.domain.uow.price_unit_of_work import PriceUnitOfWork
from src.features.prices.infra.mappers.platform_price_mapper import PlatformPriceMapper
from src.features.prices.infra.persistence.repositories.sqlalchemy_platform_price_repositories import \
    SQLAlchemyPlatformPriceRepository
from src.features.prices.infra.persistence.uow.sqlalchemy_price_unit_of_work import SQLAlchemyPriceUnitOfWork
from src.infra.persistence.connection.sqlalchemy_engine import AsyncSessionLocal


# You might want a Query Handler too
# from src.features.announcements.application.queries.get_announcements.get_announcements_query_handler import GetAnnouncementsQueryHandler
# from src.features.announcements.application.queries.get_announcements.get_announcements_query import GetAnnouncementsQuery


class PlatformPriceContainer(containers.DeclarativeContainer):
    """
    Dependency Injection Container for the Announcements Bounded Context.
    """
    # Dependencies from parent container (e.g., ApplicationContainer)
    mediator = providers.Dependency(instance_of=Mediator)
    config = providers.DelegatedSingleton(Settings)

    # Database Session - Assumes a new session per request/operation for UoW
    # IMPORTANT: If you need a single session across multiple UoWs in one request,
    # you'd need a request-scoped provider here or manage it via FastAPI Dependencies.
    db_session: providers.Factory[AsyncSession] = providers.Factory(AsyncSessionLocal)


    @staticmethod
    def create_uow(session: AsyncSession) -> PriceUnitOfWork:
        """Only static method needed - creates UoW with repository"""
        price_repo=SQLAlchemyPlatformPriceRepository(session=session)
        price_uow = SQLAlchemyPriceUnitOfWork(session=session,platform_price_repository=price_repo)
        return price_uow

    platform_prices_unit_of_work = providers.Factory(
        create_uow,
        session=db_session,
    )

    # Command Handlers
    create_platform_price_command_handler = providers.Factory(
        CreatePlatformPriceCommandHandler,
        _unit_of_work=platform_prices_unit_of_work,
        _mediator=mediator
    )

    # Query Handlers
    get_platform_prices_query_handler = providers.Factory(
        GetPlatformPricesQueryHandler,
        _unit_of_work=platform_prices_unit_of_work,
        _mediator=mediator
    )
