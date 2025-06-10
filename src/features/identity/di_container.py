# src/features/identity/di_container.py
from __future__ import annotations

from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.core.mediator.mediator import Mediator
from src.features.identity.application.commands.auth.callback_google_oauth.callback_google_oauth_command_handler import \
    CallbackGoogleOauthCommandHandler
from src.features.identity.application.commands.auth.change_password.change_password_command_handler import \
    ChangePasswordCommandHandler
from src.features.identity.application.commands.auth.verify_password.verify_password_command_handler import \
    VerifyPasswordCommandHandler
from src.features.identity.application.commands.auth.login.login_user_command_handler import LoginUserCommandHandler
from src.features.identity.application.commands.auth.logout.logout_user_command_handler import LogoutUserCommandHandler
from src.features.identity.application.commands.auth.refresh_access_token.refresh_access_token_command_handler import \
    RefreshAccessTokenCommandHandler
from src.features.identity.application.commands.auth.register_user.register_user_command_handler import \
    RegisterUserCommandHandler
from src.features.identity.application.commands.auth.request_change_email.change_email_command_handler import \
    RequestChangeEmailCommandHandler
from src.features.identity.application.commands.auth.request_reset_password.reset_password_request_command_handler import \
    RequestResetPasswordCommandHandler
from src.features.identity.application.commands.auth.verify_email.verify_email_command_handler import \
    VerifyEmailCommandHandler
from src.features.identity.application.commands.auth.verify_user.verify_user_command_handler import \
    VerifyUserCommandHandler
from src.features.identity.application.commands.profile.update_avatar.update_avatar_command_handler import \
    UpdateAvatarCommandHandler
from src.features.identity.application.commands.profile.update_me.update_me_command_handler import \
    UpdateMeCommandHandler
from src.features.identity.application.event_handlers.avatar_upload_completed_event_handler import \
    AvatarUploadCompletedEventHandler
from src.features.identity.application.queries.auth.initiate_google_oauth.initiate_google_oauth_command_handler import \
    InitiateGoogleOauthQueryHandler
from src.features.identity.application.queries.profile.get_avatar.get_avatar_command_handler import \
    GetMeAvatarQueryHandler
from src.features.identity.application.queries.profile.get_me.get_me_command_handler import GetMeQueryHandler
from src.features.identity.domain.repositories.user_unit_of_work import UserUnitOfWork
from src.features.identity.infra.persistence.repositories.sqlalchemy_user_repository import SQlAlchemyUserRepository
from src.features.identity.infra.persistence.repositories.sqlalchemy_user_unit_of_work import SQLAlchemyUserUnitOfWork
from src.features.identity.infra.services.oauth_client_service_handler import OAuthClientServiceHandler
from src.features.identity.infra.services.token_blocklist_service_handler import TokenBlocklistServiceHandler
from src.features.identity.infra.services.token_service_handler import TokenServiceHandler
from src.features.identity.infra.services.user_lookup_service_handler import UserLookupServiceHandler
from src.infra.persistence.connection.sqlalchemy_engine import AsyncSessionLocal
from src.infra.services.redis.redis_service_handler import RedisServiceHandler


class IdentityContainer(containers.DeclarativeContainer):
    # Dependencies from parent container
    mediator = providers.Dependency(instance_of=Mediator)
    config = providers.DelegatedSingleton(Settings)

    # Database
    db_session: providers.Factory[AsyncSession] = providers.Factory(AsyncSessionLocal)

    @staticmethod
    def create_uow(session: AsyncSession) -> UserUnitOfWork:
        """Only static method needed - creates UoW with repository"""
        user_repo = SQlAlchemyUserRepository(session=session)
        user_uow = SQLAlchemyUserUnitOfWork(session=session, user_repository=user_repo)
        return user_uow

    user_unit_of_work = providers.Factory(
        create_uow,
        session=db_session,
    )

    # Services
    token_service = providers.Singleton(
        TokenServiceHandler,
        secret_key=config.provided.JWT_SECRET,
        algorithm=config.provided.JWT_ALGORITHM,
        access_token_expiry=config.provided.ACCESS_TOKEN_EXPIRY_MINUTES,
        refresh_token_expiry=config.provided.REFRESH_TOKEN_EXPIRY_DAYS,
    )

    redis_service = providers.Singleton(RedisServiceHandler)

    token_blocklist_service = providers.Singleton(
        TokenBlocklistServiceHandler,
        redis_service=redis_service
    )

    oauth_client_service = providers.Singleton(
        OAuthClientServiceHandler,
        client_id=config.provided.GOOGLE_CLIENT_ID,
        client_secret=config.provided.GOOGLE_CLIENT_SECRET,
        redirect_uri=config.provided.GOOGLE_REDIRECT_URI,
    )

    user_lookup_service = providers.Factory(
        UserLookupServiceHandler,
        uow=user_unit_of_work,
    )

    # Query handlers
    initiate_google_oauth_query_handler: providers.Factory[InitiateGoogleOauthQueryHandler] = providers.Factory(
        InitiateGoogleOauthQueryHandler,
        _google_client_id=config.provided.GOOGLE_CLIENT_ID,
        _google_redirect_uri=config.provided.GOOGLE_REDIRECT_URI,
    )

    # Command handlers
    register_user_command_handler: providers.Factory[RegisterUserCommandHandler] = providers.Factory(
        RegisterUserCommandHandler,
        _unit_of_work=user_unit_of_work,
        _mediator=mediator,
    )

    verify_user_command_handler: providers.Factory[VerifyUserCommandHandler] = providers.Factory(
        VerifyUserCommandHandler,
        _unit_of_work=user_unit_of_work,
        _mediator=mediator,
    )

    login_user_command_handler: providers.Factory[LoginUserCommandHandler] = providers.Factory(
        LoginUserCommandHandler,
        _unit_of_work=user_unit_of_work,
        _token_service=token_service,
        _mediator=mediator,
        _settings=config,
    )

    logout_user_command_handler: providers.Factory[LogoutUserCommandHandler] = providers.Factory(
        LogoutUserCommandHandler,
        _blocklist_service=token_blocklist_service,
        _mediator=mediator,
    )

    refresh_access_token_command_handler: providers.Factory[RefreshAccessTokenCommandHandler] = providers.Factory(
        RefreshAccessTokenCommandHandler,
        _unit_of_work=user_unit_of_work,
        _token_service=token_service,
        _blocklist_service=token_blocklist_service,
        _mediator=mediator,
    )

    change_password_command_handler: providers.Factory[ChangePasswordCommandHandler] = providers.Factory(
        ChangePasswordCommandHandler,
        _unit_of_work=user_unit_of_work,
        _mediator=mediator,
    )

    request_reset_password_command_handler: providers.Factory[RequestResetPasswordCommandHandler] = providers.Factory(
        RequestResetPasswordCommandHandler,
        _mediator=mediator,
    )

    verify_reset_password_command_handler: providers.Factory[VerifyPasswordCommandHandler] = providers.Factory(
        VerifyPasswordCommandHandler,
        _unit_of_work=user_unit_of_work,
        _blocklist_service=token_blocklist_service,
        _mediator=mediator,
    )

    request_change_email_command_handler: providers.Factory[RequestChangeEmailCommandHandler] = providers.Factory(
        RequestChangeEmailCommandHandler,
        _unit_of_work=user_unit_of_work,
        _redis_service=redis_service,
        _mediator=mediator,
    )

    verify_email_command_handler: providers.Factory[VerifyEmailCommandHandler] = providers.Factory(
        VerifyEmailCommandHandler,
        _redis_service=redis_service,
        _unit_of_work=user_unit_of_work,
        _mediator=mediator,
    )

    callback_google_oauth_command_handler: providers.Factory[CallbackGoogleOauthCommandHandler] = providers.Factory(
        CallbackGoogleOauthCommandHandler,
        _unit_of_work=user_unit_of_work,
        _oauth_client_service=oauth_client_service,
        _token_service=token_service,
        _mediator=mediator,
    )

    update_me_command_handler: providers.Factory[UpdateMeCommandHandler] = providers.Factory(
        UpdateMeCommandHandler,
        _unit_of_work=user_unit_of_work,
        _mediator=mediator,
    )

    update_avatar_command_handler = providers.Factory(
        UpdateAvatarCommandHandler,
        _unit_of_work=user_unit_of_work,
        _mediator=mediator,
    )

    get_me_query_handler: providers.Factory[GetMeQueryHandler] = providers.Factory(
        GetMeQueryHandler,
        _unit_of_work=user_unit_of_work,
        _mediator=mediator,
    )

    get_me_avatar_query_handler = providers.Factory(
        GetMeAvatarQueryHandler,
        _unit_of_work=user_unit_of_work
    )

    # Event handlers
    avatar_upload_event_completed_handler = providers.Factory(
        AvatarUploadCompletedEventHandler,
        _unit_of_work=user_unit_of_work,
        _mediator=mediator,
    )
