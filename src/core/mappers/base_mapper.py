from src.infra.logging.setup_async_logging import async_logger as logger
from typing import Generic, TypeVar, Type

from sqlalchemy.inspection import inspect as sa_inspect

E = TypeVar('E')
M = TypeVar('M')



class BaseMapper(Generic[E, M]):
    """
    Generic ACL-protected mapper between
    - domain entity (pure Python)
    - SQLAlchemy ORM model

    Skips unknown fields safely, logs them.
    Raises on missing required entity fields.
    """

    ALIAS: dict[str, str] = {}

    def __init__(self, entity_cls: Type[E], orm_cls: Type[M]) -> None:
        self.entity_cls = entity_cls
        self.orm_cls = orm_cls

        self._entity_fields = set(getattr(entity_cls, '__annotations__', {}).keys())
        self._orm_columns = {c.key for c in sa_inspect(orm_cls).attrs}

    def to_entity(self, orm_obj: M) -> E:
        """SQLAlchemy → Entity, with ACL"""
        data = {}
        for col in self._orm_columns:
            ent_field = self._to_entity_name(col)
            if ent_field in self._entity_fields:
                data[ent_field] = getattr(orm_obj, col)
            else:
                logger.warning(f"[ACL] Ignored unexpected field from ORM: {col} → not in entity")

        # 🛑 Check: are we missing required entity fields?
        missing = self._entity_fields - data.keys()
        if missing:
            raise ValueError(f"[ACL] Missing required fields for {self.entity_cls.__name__}: {missing}")

        return self.entity_cls(**data)  # type: ignore

    def from_entity(self, ent: E) -> M:
        """Entity → SQLAlchemy"""
        kwargs = {}
        for field in self._entity_fields:
            orm_col = self._to_orm_name(field)
            if orm_col in self._orm_columns:
                kwargs[orm_col] = getattr(ent, field)
            else:
                logger.debug(f"[ACL] Skipped unknown ORM column: {orm_col}")
        return self.orm_cls(**kwargs)  # type: ignore

    def _to_entity_name(self, orm_name: str) -> str:
        return self.ALIAS.get(orm_name, orm_name)

    def _to_orm_name(self, ent_name: str) -> str:
        for k, v in self.ALIAS.items():
            if v == ent_name:
                return k
        return ent_name



