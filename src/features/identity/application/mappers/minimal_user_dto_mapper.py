# src/features/identity/application/mappers/minimal_user_dto_mapper.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import Optional, Type
from uuid import UUID

# Import your specific Entity and DTO
from src.features.identity.domain.entities.user_entity import UserEntity
from src.features.identity.api.v1.dtos.auth.login_user_dto import MinimalUserDTO # Assuming MinimalUserDTO is here



class MinimalUserDTOMapper:
    """
    Specific mapper between UserEntity and MinimalUserDTO,
    providing only essential user identification data.
    """
    entity_cls: Type[UserEntity]
    dto_cls: Type[MinimalUserDTO]

    def __init__(self, entity_cls: Type[UserEntity], dto_cls: Type[MinimalUserDTO]):
        """
        Initializes the mapper with the specific entity and DTO classes.
        """
        self.entity_cls = entity_cls
        self.dto_cls = dto_cls
        logger.debug(f"MinimalUserDTOMapper initialized for {entity_cls.__name__} and {dto_cls.__name__}")

    def to_dto(self, entity: UserEntity) -> Optional[MinimalUserDTO]:
        """Maps UserEntity domain object to MinimalUserDTO."""
        if not entity:
            logger.debug("MinimalUserDTOMapper.to_dto received None, returning None.")
            return None

        logger.debug(f"Mapping UserEntity (UID: {entity.uid}) to MinimalUserDTO.")
        try:
            dto_data = {
                "email": entity.email,
                "uid": entity.uid,
                "role": entity.role,
                "is_verified": entity.is_verified,
            }

            # Create DTO instance using the stored self.dto_cls
            dto_instance = self.dto_cls(**dto_data)
            logger.debug(f"Successfully mapped UserEntity to MinimalUserDTO (UID: {entity.uid}).")
            return dto_instance

        except Exception as e:
            logger.error(
                f"Error mapping UserEntity to MinimalUserDTO (UID: {entity.uid if entity else 'N/A'}): {e}",
                exc_info=True
            )
            # Re-raise the exception to propagate the error
            raise

    # You typically don't need a `from_dto` method for a "minimal" DTO
    # unless you intend to reconstruct a partial entity from it for specific update scenarios.
    # For most cases, a minimal DTO is read-only.