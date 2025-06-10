import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from src.config import Settings
from alembic import context
from src.infra.persistence.models.sqlalchemy_base import Base


# --- Identity ---
from src.features.identity.infra.persistence.models.user import UserORM
# --- Bot ---
from src.features.bot.infra.persistence.models.bot import BotORM
from src.features.bot.infra.persistence.models.bot_service import BotServiceORM
from src.features.bot.infra.persistence.models.bot_participant import BotParticipantORM
from src.features.bot.infra.persistence.models.bot_document import BotDocumentORM
# --- Conversations & Messages ---
from src.features.conversation.infra.persistence.models.conversation import ConversationORM
from src.features.conversation.infra.persistence.models.message import MessageORM
# --- Integrations & Telegram ---
from src.features.integrations.messengers.telegram.infra.persistence.models.telegram_account_link import TelegramAccountLinkORM
# --- Supports ---
from src.features.support.infra.persistence.models.support_orm import SupportORM
from src.features.support.infra.persistence.models.support_attachment_orm import SupportAttachmentORM
# --- Payments ---
from src.features.payments.infra.persistence.models.payment import PaymentORM
# --- Announcements ---
from src.features.announcement.infra.persistence.models.announcement_orm import AnnouncementORM
from src.infra.persistence.models.sqlalchemy_base import SQLAlchemyBase

# --- PlatformPrices ---
from src.features.prices.infra.persistence.models.platform_price_orm import PlatformPriceORM
from src.infra.persistence.models.log_orm import LogEntryORM


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
_settings = Settings()
database_url = _settings.ASYNC_DATABASE_URL
config = context.config
config.set_main_option("sqlalchemy.url", database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
