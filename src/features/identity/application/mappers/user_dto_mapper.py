# src/features/identity/application/mappers/user_dto_mapper.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import fields
from typing import Optional, Type

from src.features.identity.api.v1.dtos.profile.get_me_dto import UserDTO
# Import your specific Entity, DTO, and VO
from src.features.identity.domain.entities.user_entity import UserEntity
from src.features.identity.domain.value_objects.company_details_vo import CompanyDetails



class UserDTOMapper:
    """
    Specific mapper between PlatformUserEntity (with CompanyDetails VO)
    and the UserDTO.
    """
    entity_cls: Type[UserEntity]
    dto_cls: Type[UserDTO]

    def __init__(self, entity_cls: Type[UserEntity], dto_cls: Type[UserDTO]):
        """
        Initializes the mapper with the specific entity and DTO classes.
        """
        self.entity_cls = entity_cls
        self.dto_cls = dto_cls
        logger.debug(f"UserDTOMapper initialized for {entity_cls.__name__} and {dto_cls.__name__}")

    def to_dto(self, entity: UserEntity) -> Optional[UserDTO]:
        """Maps PlatformUserEntity domain object to UserDTO."""
        if not entity:
            logger.debug("UserDTOMapper.map_to_dto received None, returning None.")
            return None

        logger.debug(f"Mapping PlatformUserEntity (UID: {entity.uid}) to UserDTO.")
        try:
            dto_data = {
                # Base/Direct entity fields
                "uid": entity.uid,
                "created_at": getattr(entity, 'created_at', None),
                "updated_at": getattr(entity, 'updated_at', None),
                "email": entity.email,
                "role": entity.role,
                "is_verified": entity.is_verified,
                "user_type": entity.user_type, # Direct field now
                "crm_catalog_id": entity.crm_catalog_id,
                "avatar_file_url": entity.avatar_file_url,

                # Initialize company fields to None
                "is_send_docs_to_jur_address": None,
                "company_name": None,
                "field_of_activity": None,
                "BIN": None,
                "legal_address": None,
                "contact": None, # Company contact
                "phone_number": None, # Company phone
                "registration_date": None,
            }

            # Flatten CompanyDetails VO if it exists
            if entity.company_details:
                logger.debug("Flattening CompanyDetails VO to DTO data.")
                dto_data["is_send_docs_to_jur_address"] = entity.company_details.is_send_docs_to_jur_address
                dto_data["company_name"] = entity.company_details.company_name
                dto_data["field_of_activity"] = entity.company_details.field_of_activity
                dto_data["BIN"] = entity.company_details.BIN
                dto_data["legal_address"] = entity.company_details.legal_address
                dto_data["contact"] = entity.company_details.contact # Map from VO
                dto_data["phone_number"] = entity.company_details.phone_number # Map from VO
                dto_data["registration_date"] = entity.company_details.registration_date
            else:
                logger.debug("CompanyDetails VO is None, corresponding DTO fields remain None.")

            # Create DTO instance using the stored self.dto_cls
            dto_instance = self.dto_cls(**dto_data)
            logger.debug(f"Successfully mapped PlatformUserEntity to DTO (UID: {entity.uid}).")
            return dto_instance

        except Exception as e:
            print("[MAPPER CRASH] Raw dto_data:")
            print(dto_data)
            raise
        # except Exception as e:
        #     logger.error(f"Error mapping PlatformUserEntity to DTO (UID: {entity.uid if entity else 'N/A'}): {e}", exc_info=True)
        #     raise # Re-raise to signal the mapping failure

    # map_from_dto might be needed if UserDTO is used for updates
    def from_dto(self, dto: UserDTO) -> Optional[UserEntity]:
        """
        Maps UserDTO back to PlatformUserEntity.
        NOTE: This is complex as it needs to handle partial updates and
              construct the entity state, potentially requiring loading existing entity first.
              Often better handled by specific update commands/mappers.
              Provided here as a basic example assuming full data for creation/replacement.
        """
        if not dto:
             logger.debug("UserDTOMapper.map_from_dto received None, returning None.")
             return None

        logger.warning("Mapping from UserDTO back to PlatformUserEntity is complex and context-dependent.")
        try:
            # --- Extract and Create CompanyDetails VO ---
            company_details_vo = None
            company_data = {}
            company_fields = {f.name for f in fields(CompanyDetails)}
            dto_dict = dto.model_dump()
            # Explicitly check fields belonging to CompanyDetails
            for field_name in company_fields:
                if field_name in dto_dict and dto_dict[field_name] is not None:
                    company_data[field_name] = dto_dict[field_name]

            if company_data:
                company_details_vo = CompanyDetails(**company_data)

            # --- Create PlatformUserEntity ---
            # WARNING: This assumes DTO has all necessary fields for __init__
            # and doesn't handle password_hash correctly for updates.
            entity = self.entity_cls(
                uid=dto.uid, # Assumes UID is present for updates
                email=dto.email,
                role=dto.role,
                is_verified=dto.is_verified,
                user_type=dto.user_type, # Map direct field
                crm_catalog_id=dto.crm_catalog_id,
                avatar_file_url=dto.avatar_file_url,
                company_details=company_details_vo
            )
            return entity
        except Exception as e:
             logger.error(f"Error mapping UserDTO to Entity (UID: {dto.uid if dto else 'N/A'}): {e}", exc_info=True)
             raise

