from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.core.mediator.mediator import Mediator
from src.features.conversation.application.queries.get_all_conversations.get_all_conversations_impl import \
    GetAllConversationsQueryHandler
from src.features.conversation.application.queries.get_playground_conversation.get_playground_conversation_impl import \
    GetPlaygroundConversationQueryHandler
from src.features.conversation.application.queries.get_single_conversation.get_single_conversation_impl import \
    GetSingleBotConversationQueryHandler
from src.features.conversation.domain.uow.chat_unit_of_work import ConversationUnitOfWork
from src.features.conversation.infra.persistence.uow.chat_unit_of_work_impl import ConversationUnitOfWorkImpl
from src.features.conversation.infra.services.process_incoming_message_impl import ProcessIncomingMessageCommandHandler
from src.features.generation.application.services.deepseek_generation_service_impl import DeepSeekGenerationServiceImpl
from src.features.generation.application.services.stub_generation_service_impl import StubGenerationServiceImpl
from src.infra.persistence.connection.sqlalchemy_engine import AsyncSessionLocal


class ConversationContainer(containers.DeclarativeContainer):
    # Dependencies from parent
    mediator = providers.Dependency(instance_of=Mediator)
    bot_access_service = providers.Dependency()
    bot_lookup_service = providers.Dependency()
    # available_generation_services = providers.Dependency(instance_of=dict)
    config = providers.DelegatedSingleton(Settings)

    stub_generation_service = providers.Singleton(StubGenerationServiceImpl)
    deepseek_generation_service = providers.Singleton(DeepSeekGenerationServiceImpl)

    available_generation_services = providers.Singleton(
        lambda stub, deepseek: {
            "stub": stub,
            "deepseek-v2:16b": deepseek,
        },
        stub=stub_generation_service,
        deepseek=deepseek_generation_service,
    )

    db_session: providers.Factory[AsyncSession] = providers.Factory(AsyncSessionLocal)

    @staticmethod
    def create_uow(session: AsyncSession) -> ConversationUnitOfWork:
        """Only static method needed - creates UoW with repository"""
        conversation_uow = ConversationUnitOfWorkImpl(session=session)
        return conversation_uow

    conversation_unit_of_work = providers.Factory(
        create_uow,
        session=db_session,
    )

    process_incoming_message_command_impl = providers.Factory(
        ProcessIncomingMessageCommandHandler,
        chat_uow=conversation_unit_of_work,
        bot_lookup_service=bot_lookup_service,
        available_generation_services=available_generation_services,
        _mediator=mediator,
    )


    get_all_conversations_query_handler = providers.Factory(
        GetAllConversationsQueryHandler,
        _unit_of_work=conversation_unit_of_work,
        _bot_access_service=bot_access_service,
        _mediator=mediator,
    )

    get_playground_conversation_query_handler = providers.Factory(
        GetPlaygroundConversationQueryHandler,
        _unit_of_work=conversation_unit_of_work,
        _bot_access_service=bot_access_service,
        _mediator=mediator,
    )

    get_single_bot_conversation_query_handler = providers.Factory(
        GetSingleBotConversationQueryHandler,
        _unit_of_work=conversation_unit_of_work,
        _bot_access_service=bot_access_service,
        _mediator=mediator,
    )
