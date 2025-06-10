# src/features/support/domain/value_objects/support_request_enums.py

from enum import Enum


class SupportStatus(str, Enum):
    """
    Represents the current status of a support request.
    """
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    AWAITING_USER = "awaiting_user" # Waiting for user's response
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class SupportPriority(str, Enum):
    """
    Represents the urgency/priority of a support request.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SupportCategory(str, Enum):
    """
    Represents the category or type of the support request.
    """
    TECHNICAL_ISSUE = "technical_issue"
    BILLING = "billing"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    ACCOUNT_MANAGEMENT = "account_management"
    GENERAL_INQUIRY = "general_inquiry"