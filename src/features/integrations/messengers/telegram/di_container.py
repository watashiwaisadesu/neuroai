from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.core.mediator.mediator import Mediator
from src.features.bot.application.services.bot_platform_linker_service_impl import BotPlatformLinkerServiceHandler
from src.features.integrations.messengers.telegram.application.commands.reassign_telegram_link.reassign_telegram_link_command_handler import \
    ReassignTelegramLinkCommandHandler
from src.features.integrations.messengers.telegram.application.commands.request_telegram_code.request_telegram_code_impl import \
    RequestTelegramCodeCommandHandler
from src.features.integrations.messengers.telegram.application.commands.submit_telegram_code.submit_telegram_code_impl import \
    SubmitTelegramCodeCommandHandler
from src.features.integrations.messengers.telegram.application.event_handlers.stop_telegram_listener_event_handler import StopTelegramListenerHandler
from src.features.integrations.messengers.telegram.application.services.telegram_event_handler_service_impl import \
    TelegramEventHandlerServiceHandler
from src.features.integrations.messengers.telegram.application.services.telethon_client_service_impl import \
    TelethonClientServiceImpl
from src.features.integrations.messengers.telegram.domain.uow.telegram_unit_of_work import TelegramUnitOfWork
from src.features.integrations.messengers.telegram.infra.persistence.uow.telegram_unit_of_work_impl import \
    SQLAlchemyTelegramUnitOfWork
from src.infra.persistence.connection.sqlalchemy_engine import AsyncSessionLocal



class TelegramContainer(containers.DeclarativeContainer):
    # Dependencies from parent
    mediator = providers.Dependency(instance_of=Mediator)
    bot_access_service = providers.Dependency()
    bot_platform_linker_service = providers.Dependency()
    config = providers.DelegatedSingleton(Settings)


    db_session: providers.Factory[AsyncSession] = providers.Factory(AsyncSessionLocal)

    @staticmethod
    def create_uow(session: AsyncSession) -> TelegramUnitOfWork:
        """Only static method needed - creates UoW with repository"""
        telegram_uow = SQLAlchemyTelegramUnitOfWork(session=session)
        return telegram_uow

    telegram_unit_of_work = providers.Factory(
        create_uow,
        session=db_session,
    )
    # === Services ===
    telethon_service = providers.Singleton(
        TelethonClientServiceImpl,
        settings=config.provided,
    )

    telegram_event_handler_service = providers.Singleton(
        TelegramEventHandlerServiceHandler,
        telethon_service=telethon_service,
        mediator=mediator,
    )

    # === Commands ===

    request_telegram_code_command_handler = providers.Factory(
        RequestTelegramCodeCommandHandler,
        _unit_of_work=telegram_unit_of_work,
        _telethon_service=telethon_service,
        _bot_access_service=bot_access_service,
        _mediator=mediator,
        _allowed_roles=["admin", "owner"]
    )

    submit_telegram_code_command_handler = providers.Factory(
        SubmitTelegramCodeCommandHandler,
        _unit_of_work=telegram_unit_of_work,
        _telethon_service=telethon_service,
        _bot_platform_linker_service=bot_platform_linker_service,
        _event_handler_service=telegram_event_handler_service,
        _bot_access_service=bot_access_service,
        _mediator=mediator,
        _allowed_roles=["admin", "owner"],
    )

    reassign_telegram_link_command_handler = providers.Factory(
        ReassignTelegramLinkCommandHandler,
        _unit_of_work=telegram_unit_of_work,
        _bot_access_service=bot_access_service,
        _mediator=mediator,
        _telethon_service=telethon_service,
        _event_handler_service=telegram_event_handler_service,
        _allowed_roles=["admin", "owner"],
    )

    # === Events ===

    stop_telegram_event_handler = providers.Factory(
        StopTelegramListenerHandler,
        _telethon_service=telethon_service,
    )

