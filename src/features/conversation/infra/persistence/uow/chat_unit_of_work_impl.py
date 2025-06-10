# src/features/chat/infra/persistence/repositories/chat_unit_of_work_impl.py (New file)

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.features.conversation.domain.entities.message_entity import MessageEntity
from src.features.conversation.domain.repositories.message_repository import IMessageRepository
# Import interfaces and concrete repository implementation
from src.features.conversation.domain.uow.chat_unit_of_work import ConversationUnitOfWork
from src.features.conversation.domain.repositories.conversation_repository import IConversationRepository
from src.features.conversation.infra.mappers.conversation_mapper import ConversationMapper
from src.features.conversation.infra.mappers.message_mapper import MessageMapper
from src.features.conversation.infra.persistence.models.message import MessageORM
from src.features.conversation.infra.persistence.repositories.conversation_repository_impl import ConversationRepositoryImpl # Import concrete repo
from src.features.conversation.infra.persistence.repositories.message_repository_impl import MessageRepositoryImpl







class ConversationUnitOfWorkImpl(ConversationUnitOfWork):
    """Concrete implementation of the Unit of Work for Chat using SQLAlchemy."""

    _session: AsyncSession
    conversation_repository: IConversationRepository  # Use interface type hint
    message_repository: IMessageRepository

    def __init__(self, session: AsyncSession):
        self._session = session
        # Instantiate the concrete repositories with the session and mappers
        self.conversation_repository = ConversationRepositoryImpl(session)
        self.message_repository = MessageRepositoryImpl(session, MessageMapper(MessageEntity,MessageORM))
        logger.debug("ChatUnitOfWorkImpl initialized.")

    async def __aenter__(self):
        """Enter the async context manager."""
        logger.debug("Entering ChatUnitOfWork async context.")
        return self # Return the UoW instance

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager, handling commit or rollback."""
        if exc_type:
            logger.error(f"Exception occurred in Chat UoW block: {exc_type.__name__} - {exc_val}", exc_info=(exc_type, exc_val, exc_tb))
            logger.debug("Rolling back chat transaction due to exception.")
            await self.rollback() # Call internal rollback
        else:
            try:
                logger.debug("Committing chat transaction.")
                await self.commit() # Call internal commit
                logger.debug("Chat transaction committed successfully.")
            except SQLAlchemyError as e:
                logger.error(f"Error during chat transaction commit: {e}", exc_info=True)
                logger.debug("Rolling back chat transaction due to commit error.")
                await self.rollback()
                raise # Re-raise commit error
        logger.debug("Exiting ChatUnitOfWork async context.")
        await self._session.close()

    async def begin(self) -> None:
        await self._session.begin()


    async def commit(self):
        """Explicitly commit the transaction."""
        try:
            await self._session.commit()
        except SQLAlchemyError:
            await self._session.rollback() # Ensure rollback on commit failure
            raise

    async def rollback(self):
        """Explicitly rollback the transaction."""
        await self._session.rollback()
