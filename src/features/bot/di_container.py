from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.core.mediator.mediator import Mediator
from src.features.bot.application.commands.bot_documents.delete_documents.delete_documents_impl import \
    DeleteBotDocumentsCommandHandler
from src.features.bot.application.commands.bot_documents.upload_documents.upload_documents_impl import \
    UploadBotDocumentsCommandHandler
from src.features.bot.application.commands.bot_management.create_bot.create_bot_impl import CreateBotCommandHandler
from src.features.bot.application.commands.bot_management.delete_bot.delete_bot_impl import DeleteBotCommandHandler
from src.features.bot.application.commands.bot_management.duplicate_bot.duplicate_bot_impl import \
    DuplicateBotCommandHandler
from src.features.bot.application.commands.bot_management.transfer_bot.transfer_bot_impl import \
    TransferBotCommandHandler
from src.features.bot.application.commands.bot_management.update_bot.update_bot_impl import UpdateBotCommandHandler
from src.features.bot.application.commands.bot_participants.link_participant.link_participant_impl import \
    LinkBotParticipantCommandHandler
from src.features.bot.application.commands.bot_participants.unlink_participant.unlink_participant_impl import \
    UnlinkBotParticipantCommandHandler
from src.features.bot.application.commands.bot_participants.update_participant.update_participant_impl import \
    UpdateBotParticipantRoleCommandHandler
from src.features.bot.application.commands.bot_services.link_service.link_service_impl import LinkServiceCommandHandler
from src.features.bot.application.commands.bot_services.unlink_service.unlink_service_impl import \
    UnlinkServiceCommandHandler
from src.features.bot.application.commands.handle_playground_connection.handle_playground_connection_impl import \
    HandlePlaygroundConnectionCommandHandler
from src.features.bot.application.commands.playground_receive_message.playground_receive_message_handler import \
    PlaygroundReceiveMessageCommandHandler
from src.features.bot.application.commands.playground_send_message.playground_send_message_handler import \
    PlaygroundSendMessageCommandHandler
from src.features.bot.application.queries.bot_management.get_last_active_bots.get_last_active_bots_impl import \
    GetLastActiveBotsQueryHandler
from src.features.bot.application.queries.bot_management.get_user_bots.get_user_bots_impl import GetUserBotsQueryHandler
from src.features.bot.application.queries.bot_participants.get_participants.get_bot_participants_impl import \
    GetBotParticipantsQueryHandler
from src.features.bot.application.queries.bot_services.get_services.get_services_impl import GetServicesQueryHandler
from src.features.bot.application.services.bot_access_service import BotAccessService
from src.features.bot.application.services.bot_platform_linker_service_impl import BotPlatformLinkerServiceHandler
from src.features.bot.domain.repositories.bot_unit_of_work import BotUnitOfWork
from src.features.bot.infra.persistence.repositories.bot_document_repository_impl import BotDocumentRepositoryImpl
from src.features.bot.infra.persistence.repositories.bot_participant_repository_impl import BotParticipantRepositoryImpl
from src.features.bot.infra.persistence.repositories.bot_repository_impl import BotRepositoryImpl
from src.features.bot.infra.persistence.repositories.bot_service_repository_impl import BotServiceRepositoryImpl
from src.features.bot.infra.persistence.uow.bot_unit_of_work_impl import BotUnitOfWorkImpl
from src.features.bot.infra.services.bot_lookup_service_handler import BotLookupServiceHandler
from src.infra.persistence.connection.sqlalchemy_engine import AsyncSessionLocal


class BotContainer(containers.DeclarativeContainer):
    # Dependencies from parent
    mediator = providers.Dependency(instance_of=Mediator)
    user_lookup_service = providers.Dependency()
    config = providers.DelegatedSingleton(Settings)


    db_session: providers.Factory[AsyncSession] = providers.Factory(AsyncSessionLocal)

    @staticmethod
    def create_uow(session: AsyncSession) -> BotUnitOfWork:
        """Only static method needed - creates UoW with repository"""
        bot_repo = BotRepositoryImpl(session=session)
        bot_document_repo = BotDocumentRepositoryImpl(session=session)
        bot_participant_repo = BotParticipantRepositoryImpl(session=session)
        bot_service_repo = BotServiceRepositoryImpl(session=session)
        bot_uow = BotUnitOfWorkImpl(session=session,
                                     bot_repository=bot_repo,
                                     bot_service_repository=bot_service_repo,
                                     bot_document_repository=bot_document_repo,
                                     bot_participant_repository=bot_participant_repo
                                     )
        return bot_uow

    bot_unit_of_work = providers.Factory(
        create_uow,
        session=db_session,
    )

    # services
    bot_access_service = providers.Factory(
        BotAccessService,
        uow=bot_unit_of_work,
    )

    bot_lookup_service = providers.Factory(
        BotLookupServiceHandler,
        bot_uow=bot_unit_of_work,
    )

    bot_platform_linker_service = providers.Singleton(
        BotPlatformLinkerServiceHandler,
        bot_uow=bot_unit_of_work,
    )
    ### Websocket related
    handle_playground_connection_command_handler = providers.Factory(
        HandlePlaygroundConnectionCommandHandler,
        _mediator=mediator,
        _bot_access_service=bot_access_service,  # Inject bot_access_service
    )

    playground_receive_message_command_handler = providers.Factory(
        PlaygroundReceiveMessageCommandHandler,
        _mediator=mediator,
    )

    playground_send_message_command_handler = providers.Factory(
        PlaygroundSendMessageCommandHandler,
        _mediator=mediator,
    )

    # Command handlers
    create_bot_command_handler = providers.Factory(
        CreateBotCommandHandler,
        _unit_of_work=bot_unit_of_work,
        _mediator=mediator,
    )

    delete_bot_command_handler = providers.Factory(
        DeleteBotCommandHandler,
        _unit_of_work=bot_unit_of_work,
        _access_service=bot_access_service,
        _mediator=mediator,
        _allowed_roles=["owner"]
    )

    update_bot_command_handler = providers.Factory(
        UpdateBotCommandHandler,
        _unit_of_work=bot_unit_of_work,
        _access_service=bot_access_service,
        _user_lookup_service=user_lookup_service,
        _mediator=mediator,
        _allowed_roles=["editor", "admin", "owner"]
    )

    duplicate_bot_command_handler = providers.Factory(
        DuplicateBotCommandHandler,
        _unit_of_work=bot_unit_of_work,
        _access_service=bot_access_service,
        _user_lookup_service=user_lookup_service,
        _mediator=mediator,
        _allowed_roles=["admin", "owner"]
    )

    transfer_bot_command_handler = providers.Factory(
        TransferBotCommandHandler,
        _unit_of_work=bot_unit_of_work,
        _access_service=bot_access_service,
        _user_lookup_service=user_lookup_service,
        _mediator=mediator,
        _allowed_roles=["admin", "owner"]
    )

    link_bot_participant_command_handler = providers.Factory(
        LinkBotParticipantCommandHandler,
        _unit_of_work=bot_unit_of_work,
        _access_service=bot_access_service,
        _user_lookup_service=user_lookup_service,
        _mediator=mediator,
        _allowed_roles=["editor", "admin", "owner"]
    )

    unlink_bot_participant_command_handler = providers.Factory(
        UnlinkBotParticipantCommandHandler,
        _unit_of_work=bot_unit_of_work,
        _access_service=bot_access_service,
        _mediator=mediator,
        _allowed_roles=["admin","owner"]
    )

    update_bot_participant_role_command_handler = providers.Factory(
        UpdateBotParticipantRoleCommandHandler,
        _unit_of_work=bot_unit_of_work,
        _access_service=bot_access_service,
        _user_lookup_service=user_lookup_service,
        _mediator=mediator,
        _allowed_roles=["editor","admin","owner"]
    )

    link_service_command_handler = providers.Factory(
        LinkServiceCommandHandler,
        _unit_of_work=bot_unit_of_work,
        _access_service=bot_access_service,
        _mediator=mediator,
        _allowed_roles=["owner"]
    )

    unlink_service_command_handler = providers.Factory(
        UnlinkServiceCommandHandler,
        _unit_of_work=bot_unit_of_work,
        _access_service=bot_access_service,
        _mediator=mediator,
        _allowed_roles=["editor","admin", "owner"]
    )

    upload_bot_documents_command_handler = providers.Factory(
        UploadBotDocumentsCommandHandler,
        _unit_of_work=bot_unit_of_work,
        _access_service=bot_access_service,
        _mediator=mediator,
        _allowed_roles=["editor", "admin", "owner"]
    )

    delete_bot_documents_command_handler = providers.Factory(
        DeleteBotDocumentsCommandHandler,
        _unit_of_work=bot_unit_of_work,
        _access_service=bot_access_service,
        _mediator=mediator,
        _allowed_roles=["editor", "admin", "owner"]
    )

    # === Queries ===

    get_last_active_bots_query_handler = providers.Factory(
        GetLastActiveBotsQueryHandler,
        _unit_of_work=bot_unit_of_work,
        _access_service=bot_access_service,
        _user_lookup_service=user_lookup_service,
        _mediator=mediator,
        _allowed_roles=["viewer", "editor", "admin", "owner"]
    )

    get_user_bots_query_handler = providers.Factory(
        GetUserBotsQueryHandler,
        _bot_uow=bot_unit_of_work,
        _user_lookup_service=user_lookup_service,
        _access_service=bot_access_service,
        _mediator=mediator,
        _allowed_roles=["viewer","editor", "admin","owner"]
    )

    get_bot_participant_role_query_handler = providers.Factory(
        GetBotParticipantsQueryHandler,
        _bot_uow=bot_unit_of_work,
        _access_service=bot_access_service,
        _user_lookup_service=user_lookup_service,
        _mediator=mediator,
        _allowed_roles=["viewer", "editor", "admin","owner"]
    )

    get_services_query_handler = providers.Factory(
        GetServicesQueryHandler,
        _bot_uow=bot_unit_of_work,
        _access_service=bot_access_service,
        _allowed_roles=["viewer", "editor", "admin","owner"]
    )


