from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass, fields as dataclass_fields, asdict
from typing import Optional

from src.core.models.base_entity import BaseEntity
from src.features.identity.domain.events.oauth_events import OAuthUserRegisteredEvent
from src.features.identity.domain.events.user_registered_events import UserRegisteredEvent
from src.features.identity.domain.value_objects.company_details_vo import CompanyDetails




@dataclass(kw_only=True)  # eq and hash will be inherited from BaseEntity
class UserEntity(BaseEntity):
    """
    Represents a user in the system.
    Inherits UID, created_at, updated_at, and identity methods from BaseEntity.
    """
    # Fields specific to UserEntity
    email: str
    password_hash: Optional[str] = None
    user_type: str  # This was a required parameter in your original __init__

    role: str = "user"
    is_verified: bool = False
    company_details: Optional[CompanyDetails] = None  # Value Object
    crm_catalog_id: Optional[int] = None
    avatar_file_url: Optional[str] = None

    @staticmethod
    def register(
            email: str,
            password_hash: str,
            user_type: str,
            role: str = "user",
            company_details: Optional[CompanyDetails] = None,
            crm_catalog_id: Optional[int] = None,
            avatar_file_url: Optional[str] = None,
            # uid will be generated by BaseEntity's default_factory
    ) -> 'UserEntity':
        # When kw_only=True is set on UserEntity and BaseEntity, all fields must be passed as keywords.
        # BaseEntity fields (uid, created_at, updated_at) get defaults or are handled by TimestampMixin.
        user = UserEntity(
            email=email,
            password_hash=password_hash,
            user_type=user_type,
            role=role,
            is_verified=False,  # Default for new registration
            company_details=company_details,
            crm_catalog_id=crm_catalog_id,
            avatar_file_url=avatar_file_url
            # uid, created_at, updated_at are handled by BaseEntity & TimestampMixin
        )
        user.add_event(
            UserRegisteredEvent(
                user_uid=user.uid,  # user.uid is available after BaseEntity init
                email=user.email,
            )
        )
        logger.info(f"UserEntity created via register method and UserRegisteredEvent added for UID: {user.uid}")
        return user

    @staticmethod
    def register_oauth(
            email: str,
            user_type: str = "individual",
            role: str = "user",
    ) -> 'UserEntity':
        """
        Registers a new user originating from an OAuth provider (e.g., Google, Facebook).
        These users have no password and are considered immediately verified.
        """
        user = UserEntity(
            email=email,
            password_hash=None,  # Explicitly None for OAuth users
            user_type=user_type,
            role=role,
            is_verified=True,  # OAuth users are considered verified
            company_details=None,  # Assuming no company details on initial OAuth reg
            crm_catalog_id=None,
            avatar_file_url=None
        )
        # You could add a specific OAuthUserRegisteredEvent if your domain requires differentiation
        # user.add_event(OAuthUserRegisteredEvent(user_uid=user.uid, email=user.email, provider="google"))
        # user.add_event(
        #     UserRegisteredEvent(
        #         user_uid=user.uid,
        #         email=user.email,
        #     )
        # )
        user.add_event(
                OAuthUserRegisteredEvent(
                user_uid=user.uid,
                email=email,
                provider="google",
                user_type="individual"
            )
        )
        logger.info(f"UserEntity created via register_oauth method and UserRegisteredEvent added for UID: {user.uid}")
        return user

    def verify(self):
        if not self.is_verified:
            self.is_verified = True
            self.update_timestamp()  # Method from TimestampMixin

    def is_account_verified(self) -> bool:
        return self.is_verified

    def is_oauth_user(self) -> bool:
        """Check if this is an OAuth user (no password)"""
        return self.password_hash is None

    def get_role(self) -> str:
        return self.role

    def update_company_details(self, new_details: Optional[CompanyDetails]):
        """Method specifically for updating company details."""
        if self.company_details != new_details:  # Relies on CompanyDetails being a dataclass (ideally frozen) for __eq__
            self.company_details = new_details
            self.update_timestamp()

    def update_info(self, **kwargs):
        """Handles updates for simple fields AND company details."""
        company_data = {}
        other_data_changed = False
        allowed_simple_fields = {'crm_catalog_id', 'avatar_file_url', 'email', 'role'}

        # Get field names from CompanyDetails dataclass
        company_detail_field_names = {f.name for f in dataclass_fields(CompanyDetails)}

        for key, value in kwargs.items():
            if key in company_detail_field_names:
                company_data[key] = value
            elif key in allowed_simple_fields:
                if hasattr(self, key) and getattr(self, key) != value:
                    setattr(self, key, value)
                    other_data_changed = True

        if company_data:
            current_company_dict = asdict(self.company_details) if self.company_details else {}
            # Merge existing details with new data, prioritizing new data
            new_company_dict = {**current_company_dict, **company_data}
            # Filter out any keys that might have been None if CompanyDetails doesn't want them
            # or ensure CompanyDetails can handle Nones for optional fields.
            # Assuming CompanyDetails fields are Optional or have defaults for unprovided keys.

            # Only create/update if there's data, otherwise, it might clear existing if new_company_dict is empty.
            if any(new_company_dict.values()):  # Check if there's any actual data
                try:
                    self.company_details = CompanyDetails(**new_company_dict)
                except Exception as e:
                    logger.error(f"Error creating/updating CompanyDetails VO during update_info: {e}", exc_info=True)
                    raise ValueError(f"Invalid company details provided for update: {e}") from e
            elif self.company_details is not None:  # If company_data was empty, effectively clearing details
                self.company_details = None

        if company_data or other_data_changed:
            self.update_timestamp()

    def update_avatar(self, new_avatar_url: str) -> None:
        """Update user's avatar URL"""
        self.avatar_file_url = new_avatar_url
        self.update_timestamp()

    def change_email(self, new_email: str, require_reverification: bool = True):
        if not new_email or "@" not in new_email:  # Basic validation
            raise ValueError("Invalid email format provided.")
        if new_email == self.email:
            raise ValueError("New email cannot be the same as the current email.")

        self.email = new_email
        if require_reverification:
            self.is_verified = False
        self.update_timestamp()
        # Consider emitting a Domain Event here

    def change_password(self, new_password_hash: str):
        if not new_password_hash:
            raise ValueError("Password hash cannot be empty.")

        # Optional: Check if the new hash is the same as the old one
        # if new_password_hash == self.password_hash:
        #     logger.info("Attempting to set the same password hash for user %s.", self.uid)
        #     return

        self.password_hash = new_password_hash
        self.update_timestamp()





