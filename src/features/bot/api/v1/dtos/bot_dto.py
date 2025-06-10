from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class BotDTO(BaseModel):
    """
    Represents a full Data Transfer Object for a 'Bot' user.
    Mirrors many fields from UserEntity.
    """
    uid: UUID = Field(..., description="Unique identifier of the bot.")
    created_at: Optional[datetime] = Field(None, description="Timestamp when the bot was created.")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when the bot was last updated.")

    email: str = Field(..., description="Email associated with the bot account.")
    # password_hash is intentionally omitted for security reasons
    user_type: str = Field(..., description="Type of the bot user (e.g., 'bot_account').")

    role: str = Field("user", description="Role of the bot within the system.")
    is_verified: bool = Field(False, description="Whether the bot's account is verified.")
    crm_catalog_id: Optional[int] = Field(None, description="CRM catalog ID associated with the bot.")
    avatar_file_url: Optional[str] = Field(None, description="URL to the bot's avatar image.")

    # Flattened fields from CompanyDetailsVO if applicable for a bot account
    # You might consider if these are truly relevant for a 'bot' or if a simpler
    # approach is needed. I'm including them for completeness mirroring UserEntity.
    is_send_docs_to_jur_address: Optional[bool] = Field(None, description="Whether documents should be sent to the legal address for bot (if legal entity).")
    company_name: Optional[str] = Field(None, description="Company name associated with the bot (if legal entity).")
    field_of_activity: Optional[str] = Field(None, description="Field of activity for the bot's associated company.")
    BIN: Optional[str] = Field(None, description="Business Identification Number for the bot's associated company.")
    legal_address: Optional[str] = Field(None, description="Legal address for the bot's associated company.")
    contact: Optional[str] = Field(None, description="Contact person for the bot's associated company.")
    phone_number: Optional[str] = Field(None, description="Phone number for the bot's associated company.")
    registration_date: Optional[datetime] = Field(None, description="Registration date for the bot's associated company.")

    class Config:
        from_attributes = True # Enable Pydantic v2 style for mapping from attributes