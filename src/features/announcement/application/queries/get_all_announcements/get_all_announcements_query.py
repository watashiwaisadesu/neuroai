# src/features/announcements/application/queries/get_all_announcements/get_all_announcements_query.py

from dataclasses import dataclass
from src.core.mediator.query import BaseQuery


@dataclass(frozen=True)
class GetAllAnnouncementsQuery(BaseQuery):
    """
    Query to retrieve all system announcements.
    """
    pass