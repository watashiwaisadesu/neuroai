from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any


class BaseQuery(ABC):
    """Base class for all queries"""
    pass

QT = TypeVar("QT", bound=BaseQuery)  # Query Type
QR = TypeVar("QR", bound=Any)  # Query Result


class BaseQueryHandler(ABC, Generic[QT, QR]):
    """Base class for all query handlers"""

    @abstractmethod
    async def __call__(self, query: QT) -> QR:
        """Handle the query"""
        pass