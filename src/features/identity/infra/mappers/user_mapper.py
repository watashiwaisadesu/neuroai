from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import Optional, Type

from src.features.identity.domain.entities.user_entity import UserEntity
from src.features.identity.infra.persistence.models.user import UserORM
from src.features.identity.domain.value_objects.company_details_vo import CompanyDetails




class UserMapper:
    """
    Specific mapper between PlatformUserEntity (with CompanyDetails VO)
    and the PlatformUserORM model.
    """
    # Store the classes if needed, though the methods below are explicit
    entity_cls: Type[UserEntity]
    orm_cls: Type[UserORM]

    def __init__(self, entity_cls: Type[UserEntity], orm_cls: Type[UserORM]):
        """
        Initializes the mapper with the specific entity and ORM classes.
        """
        self.entity_cls = entity_cls
        self.orm_cls = orm_cls
        logger.debug(f"PlatformUserMapper initialized for {entity_cls.__name__} and {orm_cls.__name__}")

    def to_entity(self, orm_obj: UserORM) -> Optional[UserEntity]:
        """Maps PlatformUserORM object to PlatformUserEntity domain object."""
        if not orm_obj:
            logger.debug("PlatformUserMapper.to_entity received None, returning None.")
            return None

        logger.debug(f"Mapping ORM object (UID: {orm_obj.uid}) to PlatformUserEntity.")
        try:
            # Construct CompanyDetails VO if relevant fields exist
            company_details = None
            # Check a key field like company_name or user_type to decide if details exist
            # Ensure required fields for CompanyDetails are checked if they can be None in ORM but not VO
            if orm_obj.user_type or orm_obj.company_name or orm_obj.BIN:
                logger.debug("Constructing CompanyDetails VO.")
                company_details = CompanyDetails(
                    is_send_docs_to_jur_address=orm_obj.is_send_docs_to_jur_address or False, # Handle None from DB
                    company_name=orm_obj.company_name,
                    field_of_activity=orm_obj.field_of_activity,
                    BIN=orm_obj.BIN,
                    contact=orm_obj.contact,
                    phone_number=orm_obj.phone_number,
                    legal_address=orm_obj.legal_address,
                    registration_date=orm_obj.registration_date
                )
            else:
                logger.debug("No relevant company details found in ORM, CompanyDetails VO will be None.")


            # Create PlatformUserEntity instance using the stored self.entity_cls
            logger.debug("Constructing PlatformUserEntity.")
            entity = self.entity_cls( # Use self.entity_cls here
                # Base entity fields
                user_type=orm_obj.user_type,
                uid=orm_obj.uid,

                # Core PlatformUser fields
                email=orm_obj.email,
                password_hash=orm_obj.password_hash,
                role=orm_obj.role,
                is_verified=orm_obj.is_verified,
                crm_catalog_id=orm_obj.crm_catalog_id,
                avatar_file_url=orm_obj.avatar_file_url,

                # Value Object
                company_details=company_details # Assign the VO (or None)
            )
            logger.debug(f"Successfully mapped ORM to PlatformUserEntity (UID: {entity.uid}).")
            return entity

        except Exception as e:
            logger.error(f"Error mapping PlatformUserORM to Entity (UID: {orm_obj.uid if orm_obj else 'N/A'}): {e}", exc_info=True)
            raise # Re-raise to signal the mapping failure

    def from_entity(self, entity: UserEntity) -> Optional[UserORM]:
        """Maps PlatformUserEntity domain object to PlatformUserORM object."""
        if not entity:
            logger.debug("PlatformUserMapper.from_entity received None, returning None.")
            return None

        logger.debug(f"Mapping PlatformUserEntity (UID: {entity.uid}) to ORM object.")
        try:
            orm_data = {
                # Base entity fields
                "uid": entity.uid,
                "created_at": getattr(entity, 'created_at', None), # Use getattr for safety if base class might not have it
                "updated_at": getattr(entity, 'updated_at', None),

                # Core PlatformUser fields
                "user_type": entity.user_type,
                "email": entity.email,
                "password_hash": entity.password_hash,
                "role": entity.role,
                "is_verified": entity.is_verified,
                "crm_catalog_id": entity.crm_catalog_id,
                "avatar_file_url": entity.avatar_file_url,
            }

            # Flatten CompanyDetails VO if it exists
            if entity.company_details:
                logger.debug("Flattening CompanyDetails VO to ORM data.")
                # Ensure all fields expected by ORM are included from VO
                orm_data["is_send_docs_to_jur_address"] = entity.company_details.is_send_docs_to_jur_address
                orm_data["company_name"] = entity.company_details.company_name
                orm_data["field_of_activity"] = entity.company_details.field_of_activity
                orm_data["contact"] = entity.company_details.contact
                orm_data["phone_number"] = entity.company_details.phone_number
                orm_data["BIN"] = entity.company_details.BIN
                orm_data["legal_address"] = entity.company_details.legal_address
                orm_data["registration_date"] = entity.company_details.registration_date
            else:
                # Ensure ORM fields are set to None or default if VO is None
                # and the ORM columns are nullable
                logger.debug("CompanyDetails VO is None, setting corresponding ORM fields to None.")
                orm_data["is_send_docs_to_jur_address"] = None # Or default False if DB requires/prefers
                orm_data["company_name"] = None
                orm_data["field_of_activity"] = None
                orm_data["BIN"] = None
                orm_data["contact"] = None
                orm_data["phone_number"] = None
                orm_data["legal_address"] = None
                orm_data["registration_date"] = None

            # Create ORM instance using the stored self.orm_cls
            orm_instance = self.orm_cls(**orm_data) # Use self.orm_cls here
            logger.debug(f"Successfully mapped PlatformUserEntity to ORM instance (UID: {entity.uid}).")
            return orm_instance

        except Exception as e:
            logger.error(f"Error mapping PlatformUserEntity to ORM (UID: {entity.uid if entity else 'N/A'}): {e}", exc_info=True)
            raise # Re-raise to signal the mapping failure




