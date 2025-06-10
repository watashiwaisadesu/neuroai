import uuid
from typing import Optional
from dataclasses import dataclass, field # Import dataclass and field
from datetime import datetime, timezone # Import for BaseEntity defaults

from src.core.models.base_entity import BaseEntity
from src.features.bot.domain.value_objects.ai_configuration_vo import AIConfigurationSettings
from src.features.bot.domain.value_objects.bot_quota_vo import BotQuota
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger



class BotStatus: # Simple Enum-like class for status
    DRAFT = "draft"
    ACTIVE = "active"
    SUSPENDED = "suspended"

@dataclass
class BotEntity(BaseEntity):
    """
    Aggregate Root for the Bot concept. Includes all relevant fields.
    Refactored to use dataclass for conciseness and clarity.
    """
    # Core Identity & Type - these are now dataclass fields
    # Using field(init=False) for properties that are set via __post_init__ or methods,
    # but for simple attributes that are part of the constructor, keep them as regular fields.
    # The '_' prefix indicates a convention for attributes accessed via properties.
    user_uid: uuid.UUID
    bot_type: str

    # Value Objects (assuming these are dataclasses or regular classes)
    ai_settings: AIConfigurationSettings
    quota: BotQuota

    # Other Attributes with default values
    name: Optional[str] = None
    status: str = BotStatus.DRAFT
    tariff: Optional[str] = None
    auto_deduction: bool = False
    crm_lead_id: Optional[int] = None

    def __post_init__(self):
        """
        Initializes the BaseEntity and performs initial state validation.
        Called automatically after the dataclass's __init__ is done.
        """
        super().__post_init__() # Call __post_init__ of BaseEntity for its own validation/setup

        # --- Initial State Validation ---
        if not self.user_uid:
            raise ValueError("Bot user_uid cannot be empty.")
        if not self.bot_type:
            raise ValueError("Bot type cannot be empty.")
        if self.status not in [BotStatus.DRAFT, BotStatus.ACTIVE, BotStatus.SUSPENDED]:
             raise ValueError(f"Invalid initial status: {self.status}")
        # Add other validation as needed for ai_settings, quota, etc.

    # --- Behavioral Methods ---

    def update_ai_settings(self, new_settings: AIConfigurationSettings):
        """Updates the AI configuration settings for the bot."""
        self.ai_settings = new_settings
        self.update_timestamp() # Update timestamp on change

    def deduct_tokens(self, amount: int):
        """Deducts a specified amount of tokens from the bot's quota."""
        # Ensure quota object exists and has deduct method
        if not self.quota:
            raise ValueError("Bot has no quota defined.")
        self.quota.deduct(amount)
        self.update_timestamp() # Update timestamp on change

    def activate(self):
        """Activates the bot, setting its status to ACTIVE."""
        if self.status == BotStatus.ACTIVE:
            logger.warning(f"Bot {self.uid} is already active.")
            return

        self.status = BotStatus.ACTIVE
        self.update_timestamp() # Update timestamp on change
        logger.info(f"Bot {self.uid} status changed to ACTIVE.")

    def suspend(self):
        """Suspends the bot, setting its status to SUSPENDED."""
        if self.status == BotStatus.SUSPENDED:
            logger.warning(f"Bot {self.uid} is already suspended.")
            return

        self.status = BotStatus.SUSPENDED
        self.update_timestamp() # Update timestamp on change
        logger.info(f"Bot {self.uid} status changed to SUSPENDED.")

    def update_token_limit(self, new_limit: int):
        """Updates the token limit for the bot's quota."""
        if new_limit < 0:
            raise ValueError("Token limit cannot be negative.")
        # Create a new BotQuota instance to ensure immutability if BotQuota is a Value Object
        # and to reset tokens_left to the new limit (common business rule).
        self.quota = BotQuota(token_limit=new_limit, tokens_left=new_limit)
        self.update_timestamp()
        logger.info(f"Bot {self.uid} token limit updated to {new_limit}.")

    def update_details(self, **kwargs):
        """
        Updates general details of the bot.
        Uses kwargs for flexibility but should be used with caution for known fields.
        """
        allowed_fields = ['name', 'tariff', 'auto_deduction', 'crm_lead_id'] # Note: bot_type is usually immutable post-creation
        updated = False
        for key, value in kwargs.items():
            if key in allowed_fields:
                # Basic validation for some fields can go here if needed
                if key == 'bot_type' and not isinstance(value, str): # Example: strict type check for bot_type
                    raise TypeError(f"Invalid type for bot_type: expected str, got {type(value)}")

                if getattr(self, key) != value: # Only update if value is different
                    setattr(self, key, value)
                    updated = True
            else:
                logger.warning(f"Attempted to update unknown or disallowed field: {key} for Bot {self.uid}.")

        if updated:
            self.update_timestamp()
            logger.info(f"Bot {self.uid} details updated.")


    def transfer_ownership(self, new_owner_uid: uuid.UUID):
        """
        Transfers the ownership of the bot to a new user.
        Raises ValueError if the new owner is the same as the current owner.
        """
        if not isinstance(new_owner_uid, uuid.UUID):
            raise TypeError("new_owner_uid must be a valid UUID.")
        if new_owner_uid == self.user_uid:
            raise ValueError(f"New owner {new_owner_uid} is the same as the current owner {self.user_uid}.")

        logger.info(f"Bot {self.uid}: Transferring ownership from {self.user_uid} to {new_owner_uid}.")
        self.user_uid = new_owner_uid # Change owner
        self.update_timestamp() # Update modification time
        logger.info(f"Bot {self.uid} ownership transferred to {new_owner_uid}.")