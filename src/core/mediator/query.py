# src/core/mediator/query.py
from abc import ABC
from typing import Dict, Callable

from src.core.base.query import BaseQuery, BaseQueryHandler


class QueryMediator(ABC):
    _query_providers: Dict[type, Callable[[], BaseQueryHandler]] = {}
