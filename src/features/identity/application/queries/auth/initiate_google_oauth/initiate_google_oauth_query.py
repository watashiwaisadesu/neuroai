# src/features/identity/application/queries/auth/initiate_google_oauth/initiate_google_oauth_query.py
from dataclasses import dataclass
from typing import Optional

from src.core.base.query import BaseQuery


@dataclass
class InitiateGoogleOauthQuery(BaseQuery):
    """Query to initiate Google OAuth flow"""
    # No parameters needed for OAuth initiation
    pass