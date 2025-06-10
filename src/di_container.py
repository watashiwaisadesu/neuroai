from dependency_injector import containers, providers

from src.config import Settings
from src.core.mediator.mediator import Mediator
from src.features.announcement.application.commands.create_announcement.create_announcement_command import \
    CreateAnnouncementCommand
from src.features.announcement.application.queries.get_all_announcements.get_all_announcements_query import \
    GetAllAnnouncementsQuery
from src.features.announcement.di_container import AnnouncementContainer
from src.features.bot.application.commands.bot_documents.delete_documents.delete_documents_command import \
    DeleteBotDocumentsCommand
from src.features.bot.application.commands.bot_documents.upload_documents.upload_documents_command import \
    UploadBotDocumentsCommand
from src.features.bot.application.commands.bot_management.create_bot.create_bot_command import CreateBotCommand
from src.features.bot.application.commands.bot_management.delete_bot.delete_bot_command import DeleteBotCommand
from src.features.bot.application.commands.bot_management.duplicate_bot.duplicate_bot_command import DuplicateBotCommand
from src.features.bot.application.commands.bot_management.transfer_bot.transfer_bot_command import TransferBotCommand
from src.features.bot.application.commands.bot_management.update_bot.update_bot_command import UpdateBotCommand
from src.features.bot.application.commands.bot_participants.link_participant.link_participant_command import \
    LinkBotParticipantCommand
from src.features.bot.application.commands.bot_participants.unlink_participant.unlink_participant_command import \
    UnlinkBotParticipantCommand
from src.features.bot.application.commands.bot_participants.update_participant.update_participant_command import \
    UpdateBotParticipantRoleCommand
from src.features.bot.application.commands.bot_services.link_service.link_service_command import LinkServiceCommand
from src.features.bot.application.commands.bot_services.unlink_service.unlink_service_command import \
    UnlinkServiceCommand
from src.features.bot.application.commands.handle_playground_connection.handle_playground_connection_command import \
    HandlePlaygroundConnectionCommand
from src.features.bot.application.commands.playground_receive_message.playground_receive_message_command import \
    PlaygroundReceiveMessageCommand
from src.features.bot.application.commands.playground_send_message.playground_send_message_command import \
    PlaygroundSendMessageCommand
from src.features.bot.application.event_handlers.bot_expiry_handler import BotExpiryHandler
from src.features.bot.application.queries.bot_management.get_last_active_bots.get_last_active_bots_query import \
    GetLastActiveBotsQuery
from src.features.bot.application.queries.bot_management.get_user_bots.get_user_bots_query import GetUserBotsQuery
from src.features.bot.application.queries.bot_participants.get_participants.get_bot_participants_query import \
    GetBotParticipantsQuery
from src.features.bot.application.queries.bot_services.get_services.get_services_query import GetServicesQuery
from src.features.bot.di_container import BotContainer
from src.features.bot.domain.events.bot_events import BotExpirySetEvent
from src.features.bot.domain.events.service_unlinked_event import ServiceUnlinkedEvent
from src.features.conversation.application.queries.get_all_conversations.get_all_conversations_query import \
    GetAllConversationsQuery
from src.features.conversation.application.queries.get_playground_conversation.get_playground_conversation_query import \
    GetPlaygroundConversationQuery
from src.features.conversation.application.queries.get_single_conversation.get_single_conversation_query import \
    GetSingleBotConversationQuery
from src.features.conversation.di_container import ConversationContainer
from src.features.conversation.domain.services.process_incoming_message_command import ProcessIncomingMessageCommand
from src.features.identity.application.commands.auth.callback_google_oauth.callback_google_oauth_command import \
    CallbackGoogleOauthCommand
from src.features.identity.application.commands.auth.change_password.change_password_command import \
    ChangePasswordCommand
from src.features.identity.application.commands.auth.verify_password.verify_password_command import \
    VerifyPasswordCommand
from src.features.identity.application.commands.auth.login.login_user_command import LoginUserCommand
from src.features.identity.application.commands.auth.logout.logout_user_command import LogoutUserCommand
from src.features.identity.application.commands.auth.refresh_access_token.refresh_access_token_command import \
    RefreshTokenUserCommand
from src.features.identity.application.commands.auth.register_user.register_user_command import RegisterUserCommand
from src.features.identity.application.commands.auth.request_change_email.change_email_command import \
    RequestChangeEmailCommand
from src.features.identity.application.commands.auth.request_reset_password.reset_password_request_command import \
    RequestResetPasswordCommand
from src.features.identity.application.commands.auth.verify_email.verify_email_command import VerifyEmailCommand
from src.features.identity.application.commands.auth.verify_user.verify_user_command import VerifyUserCommand
from src.features.identity.application.commands.profile.update_avatar.update_avatar_command import UpdateAvatarCommand
from src.features.identity.application.commands.profile.update_me.update_me_command import UpdateMeCommand
from src.features.identity.application.queries.auth.initiate_google_oauth.initiate_google_oauth_query import \
    InitiateGoogleOauthQuery
from src.features.identity.application.queries.profile.get_avatar.get_me_avatar_query import GetMeAvatarQuery
from src.features.identity.application.queries.profile.get_me.get_me_query import GetMeQuery
# containers
from src.features.identity.di_container import IdentityContainer
from src.features.identity.domain.events.email_change_events import EmailChangeRequestedEvent
from src.features.identity.domain.events.oauth_events import OAuthUserRegisteredEvent, OAuthLoginSuccessfulEvent
from src.features.identity.domain.events.password_reset_request_events import PasswordResetRequestedEvent
from src.features.identity.domain.events.user_avatar_events import UserAvatarUploadRequestedEvent, \
    UserAvatarUploadCompletedEvent
from src.features.identity.domain.events.user_registered_events import UserRegisteredEvent
from src.features.integrations.messengers.telegram.application.commands.reassign_telegram_link.reassign_telegram_link_command import \
    ReassignTelegramLinkCommand
from src.features.integrations.messengers.telegram.application.commands.request_telegram_code.request_telegram_code_command import \
    RequestTelegramCodeCommand
from src.features.integrations.messengers.telegram.application.commands.submit_telegram_code.submit_telegram_code_command import \
    SubmitTelegramCodeCommand
from src.features.integrations.messengers.telegram.di_container import TelegramContainer
from src.features.notification.di_container import NotificationContainer
from src.features.prices.application.commands.create_platfrom_price_command import CreatePlatformPriceCommand
from src.features.prices.application.queries.get_platform_prices_query import GetPlatformPricesQuery
from src.features.prices.di_container import PlatformPriceContainer
from src.features.support.application.commands.create_support.create_support_command import \
    CreateSupportCommand
from src.features.support.application.queries.get_supports.get_supports_query import \
    GetSupportsQuery
from src.features.support.di_container import SupportContainer
from src.features.support.domain.events.support_requested_event import SupportRequestedEvent
from src.features.support.domain.events.support_uploaded_event import SupportUploadedEvent
from src.infra.services.redis.redis_service_handler import RedisServiceHandler
from src.infra.services.s3.event_handlers.avatar_upload_event_handler import AvatarUploadRequestedEventHandler
from src.infra.services.s3.event_handlers.support_requested_event_handler import SupportRequestedEventHandler
from src.infra.services.s3.s3_service_impl import S3UploaderServiceHandler


class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Singleton(Settings)
    mediator = providers.Singleton(Mediator)
    redis_service = providers.Singleton(RedisServiceHandler)

    # # Add containers as attributes to store instances
    identity_container: IdentityContainer = None
    notification_container: NotificationContainer = None
    bot_container: BotContainer = None
    announcement_container: AnnouncementContainer = None
    support_container: SupportContainer = None
    conversation_container: ConversationContainer = None
    telegram_container: TelegramContainer = None

    s3_uploader = providers.Singleton(
        S3UploaderServiceHandler,
    )

    avatar_upload_event_handler = providers.Factory(
        AvatarUploadRequestedEventHandler,
        _s3_service=s3_uploader,
        _mediator=mediator,
    )

    support_requested_event_handler = providers.Factory(
        SupportRequestedEventHandler,
        _s3_service=s3_uploader,
        _mediator=mediator,
    )

    bot_expiry_handler = providers.Factory(
        BotExpiryHandler,
        _redis_service=redis_service,
    )


async def initialize_application_container(app_container: ApplicationContainer) -> None:
    mediator_instance = app_container.mediator()


async def initialize_identity_container(app_container: ApplicationContainer) -> None:
    """Initialize the identity container by registering all handlers with the mediator"""
    try:
        # Share the same config and mediator instances
        identity_container = IdentityContainer(
            mediator=app_container.mediator()
        )
        # # STORE THE IDENTITY CONTAINER IN APP_CONTAINER
        app_container.identity_container = identity_container

        identity_container.config.override(app_container.config)

        # Get the mediator instance
        mediator_instance = app_container.mediator()

        # Register command handlers
        mediator_instance.register_command_handler(
            command_type=RegisterUserCommand,
            provider=identity_container.register_user_command_handler,
        )

        mediator_instance.register_command_handler(
            command_type=VerifyUserCommand,
            provider=identity_container.verify_user_command_handler,
        )

        mediator_instance.register_command_handler(
            command_type=LoginUserCommand,
            provider=identity_container.login_user_command_handler,
        )

        mediator_instance.register_command_handler(
            command_type=LogoutUserCommand,
            provider=identity_container.logout_user_command_handler,
        )

        mediator_instance.register_command_handler(
            command_type=RefreshTokenUserCommand,
            provider=identity_container.refresh_access_token_command_handler,
        )

        mediator_instance.register_command_handler(
            command_type=ChangePasswordCommand,
            provider=identity_container.change_password_command_handler,
        )

        mediator_instance.register_command_handler(
            command_type=RequestResetPasswordCommand,
            provider=identity_container.request_reset_password_command_handler,
        )

        mediator_instance.register_command_handler(
            command_type=VerifyPasswordCommand,
            provider=identity_container.verify_reset_password_command_handler,
        )

        mediator_instance.register_command_handler(
            command_type=RequestChangeEmailCommand,
            provider=identity_container.request_change_email_command_handler,
        )

        mediator_instance.register_command_handler(
            command_type=VerifyEmailCommand,
            provider=identity_container.verify_email_command_handler,
        )

        mediator_instance.register_query_handler(
            query_type=InitiateGoogleOauthQuery,
            provider=identity_container.initiate_google_oauth_query_handler,
        )

        mediator_instance.register_command_handler(
            command_type=CallbackGoogleOauthCommand,
            provider=identity_container.callback_google_oauth_command_handler,
        )

        mediator_instance.register_command_handler(
            command_type=UpdateMeCommand,
            provider=identity_container.update_me_command_handler,
        )

        mediator_instance.register_command_handler(
            command_type=UpdateAvatarCommand,
            provider=identity_container.update_avatar_command_handler,
        )

        mediator_instance.register_query_handler(
            query_type=GetMeQuery,
            provider=identity_container.get_me_query_handler,
        )

        mediator_instance.register_query_handler(
            query_type=GetMeAvatarQuery,
            provider=identity_container.get_me_avatar_query_handler,
        )

        # Events to register
        mediator_instance.register_event_handlers(
            event_type=UserAvatarUploadCompletedEvent,
            providers=[identity_container.avatar_upload_event_completed_handler]
        )

        mediator_instance.register_event_handlers(
            event_type=UserAvatarUploadRequestedEvent,
            providers=[app_container.avatar_upload_event_handler]
        )

    except Exception as e:
        print(f"[ApplicationContainer] Error during initialization: {e}")
        raise


async def initialize_notification_container(app_container) -> None:
    """Initialize the notification container by registering all handlers with the mediator"""
    try:
        # Create and initialize the notification container
        notification_container = NotificationContainer(
            mediator=app_container.mediator()
        )
        notification_container.config.override(app_container.config)

        # # STORE THE NOTIFICATION CONTAINER IN APP_CONTAINER
        app_container.notification_container = notification_container

        # Get the mediator instance
        mediator_instance = app_container.mediator()

        mediator_instance.register_event_handlers(
            event_type=UserRegisteredEvent,
            providers=[notification_container.send_user_verification_email_event_handler]
        )

        mediator_instance.register_event_handlers(
            event_type=PasswordResetRequestedEvent,
            providers=[notification_container.send_password_reset_email_event_handler]
        )

        mediator_instance.register_event_handlers(
            event_type=EmailChangeRequestedEvent,
            providers=[notification_container.send_email_change_confirmation_event_handler]
        )

        mediator_instance.register_event_handlers(
            event_type=OAuthUserRegisteredEvent,
            providers=[notification_container.oauth_user_created_event_handler]
        )

        mediator_instance.register_event_handlers(
            event_type=OAuthLoginSuccessfulEvent,
            providers=[notification_container.oauth_login_successful_event_handler]
        )
    except Exception as e:
        print(f"[NotificationContainer] Error during initialization: {e}")
        raise


async def initialize_bot_container(app_container: ApplicationContainer) -> None:
    identity_container = app_container.identity_container
    bot_container = BotContainer(
        mediator=app_container.mediator(),
        user_lookup_service=identity_container.user_lookup_service(),
    )

    # # Store the bot container
    app_container.bot_container = bot_container

    mediator = app_container.mediator()
    # websocket
    mediator.register_command_handler(
        HandlePlaygroundConnectionCommand,
        bot_container.handle_playground_connection_command_handler
    )

    mediator.register_command_handler(
        PlaygroundReceiveMessageCommand,
        bot_container.playground_receive_message_command_handler
    )
    mediator.register_command_handler(
        PlaygroundSendMessageCommand,
        bot_container.playground_send_message_command_handler
    )

    # Register command handlers
    mediator.register_command_handler(
        CreateBotCommand,
        bot_container.create_bot_command_handler
    )

    mediator.register_command_handler(
        DeleteBotCommand,
        bot_container.delete_bot_command_handler
    )

    mediator.register_command_handler(
        UpdateBotCommand,
        bot_container.update_bot_command_handler
    )

    mediator.register_command_handler(
        DuplicateBotCommand,
        bot_container.duplicate_bot_command_handler
    )

    mediator.register_command_handler(
        TransferBotCommand,
        bot_container.transfer_bot_command_handler
    )

    mediator.register_command_handler(
        LinkBotParticipantCommand,
        bot_container.link_bot_participant_command_handler
    )

    mediator.register_command_handler(
        UnlinkBotParticipantCommand,
        bot_container.unlink_bot_participant_command_handler
    )

    mediator.register_command_handler(
        UpdateBotParticipantRoleCommand,
        bot_container.update_bot_participant_role_command_handler
    )

    mediator.register_command_handler(
        LinkServiceCommand,
        bot_container.link_service_command_handler
    )

    mediator.register_command_handler(
        UnlinkServiceCommand,
        bot_container.unlink_service_command_handler
    )

    mediator.register_command_handler(
        UploadBotDocumentsCommand,
        bot_container.upload_bot_documents_command_handler
    )

    mediator.register_command_handler(
        DeleteBotDocumentsCommand,
        bot_container.delete_bot_documents_command_handler
    )
    # Register queries

    mediator.register_query_handler(
        GetUserBotsQuery,
        bot_container.get_user_bots_query_handler
    )

    mediator.register_query_handler(
        GetLastActiveBotsQuery,
        bot_container.get_last_active_bots_query_handler
    )

    mediator.register_query_handler(
        GetBotParticipantsQuery,
        bot_container.get_bot_participant_role_query_handler
    )

    mediator.register_query_handler(
        GetServicesQuery,
        bot_container.get_services_query_handler
    )

    # Register domain event handler

    # Register infrastructure event handlers

    mediator.register_event_handlers(
        event_type=BotExpirySetEvent,
        providers=[app_container.bot_expiry_handler]
    )


async def initialize_conversation_container(app_container: ApplicationContainer) -> None:
    bot_container = app_container.bot_container
    conversation_container = ConversationContainer(
        mediator=app_container.mediator(),
        bot_access_service=bot_container.bot_access_service(),
        bot_lookup_service=bot_container.bot_lookup_service(),
    )

    # # Store the bot container
    app_container.conversation_container = conversation_container

    mediator = app_container.mediator()

    mediator.register_command_handler(
        ProcessIncomingMessageCommand,
        conversation_container.process_incoming_message_command_impl
    )

    mediator.register_query_handler(
        GetAllConversationsQuery,
        conversation_container.get_all_conversations_query_handler
    )

    mediator.register_query_handler(
        GetPlaygroundConversationQuery,
        conversation_container.get_playground_conversation_query_handler
    )

    mediator.register_query_handler(
        GetSingleBotConversationQuery,
        conversation_container.get_single_bot_conversation_query_handler
    )


async def initialize_telegram_container(app_container: ApplicationContainer) -> None:
    bot_container = app_container.bot_container
    telegram_container = TelegramContainer(
        mediator=app_container.mediator(),
        bot_access_service=bot_container.bot_access_service(),
        bot_platform_linker_service=bot_container.bot_platform_linker_service(),
    )

    # # Store the bot container
    app_container.telegram_container = telegram_container

    mediator = app_container.mediator()

    mediator.register_command_handler(
        RequestTelegramCodeCommand,
        telegram_container.request_telegram_code_command_handler
    )

    mediator.register_command_handler(
        SubmitTelegramCodeCommand,
        telegram_container.submit_telegram_code_command_handler,
    )

    mediator.register_command_handler(
        ReassignTelegramLinkCommand,
        telegram_container.reassign_telegram_link_command_handler
    )

    mediator.register_event_handlers(
        event_type=ServiceUnlinkedEvent,
        providers=[telegram_container.stop_telegram_event_handler]
    )


async def initialize_announcement_container(app_container: ApplicationContainer) -> None:
    """Initialize the announcement container by registering all handlers with the mediator"""
    try:
        # Share the same config and mediator instances
        announcement_container = AnnouncementContainer(
            mediator=app_container.mediator()
        )

        # # STORE THE ANNOUNCEMENT CONTAINER IN APP_CONTAINER
        app_container.announcement_container = announcement_container

        announcement_container.config.override(app_container.config)

        # Get the mediator instance
        mediator_instance = app_container.mediator()

        # Register command handlers
        mediator_instance.register_command_handler(
            command_type=CreateAnnouncementCommand,
            provider=announcement_container.create_announcement_command_handler,
        )

        mediator_instance.register_query_handler(
            query_type=GetAllAnnouncementsQuery,
            provider=announcement_container.get_all_announcement_query_handler,
        )
    except Exception as e:
        print(f"[ApplicationContainer] Error during initialization: {e}")
        raise


async def initialize_support_container(app_container: ApplicationContainer) -> None:
    try:
        # Share the same config and mediator instances
        identity_container = app_container.identity_container
        support_container = SupportContainer(
            mediator=app_container.mediator(),
            user_lookup_service=identity_container.user_lookup_service(),
        )

        # # STORE THE ANNOUNCEMENT CONTAINER IN APP_CONTAINER
        app_container.support_container = support_container

        support_container.config.override(app_container.config)

        # Get the mediator instance
        mediator_instance = app_container.mediator()

        # Register command handlers
        mediator_instance.register_command_handler(
            command_type=CreateSupportCommand,
            provider=support_container.create_support_command_handler,
        )

        mediator_instance.register_query_handler(
            query_type=GetSupportsQuery,
            provider=support_container.get_supports_query_handler,
        )

        mediator_instance.register_event_handlers(
            event_type=SupportRequestedEvent,
            providers=[app_container.support_requested_event_handler]
        )

        mediator_instance.register_event_handlers(
            event_type=SupportUploadedEvent,
            providers=[support_container.support_uploaded_event_handler]
        )

    except Exception as e:
        print(f"[ApplicationContainer] Error during initialization: {e}")
        raise



async def initialize_platform_price_container(app_container: ApplicationContainer) -> None:
    """Initialize the announcement container by registering all handlers with the mediator"""
    try:
        # Share the same config and mediator instances
        platform_price_container = PlatformPriceContainer(
            mediator=app_container.mediator()
        )

        # # STORE THE ANNOUNCEMENT CONTAINER IN APP_CONTAINER
        app_container.announcement_container = platform_price_container

        platform_price_container.config.override(app_container.config)

        # Get the mediator instance
        mediator_instance = app_container.mediator()

        # Register command handlers
        mediator_instance.register_command_handler(
            command_type=CreatePlatformPriceCommand,
            provider=platform_price_container.create_platform_price_command_handler,
        )

        mediator_instance.register_query_handler(
            query_type=GetPlatformPricesQuery,
            provider=platform_price_container.get_platform_prices_query_handler,
        )
    except Exception as e:
        print(f"[ApplicationContainer] Error during initialization: {e}")
        raise



