# src/core/mappers/base_dto_mapper.py
from src.infra.logging.setup_async_logging import async_logger as logger
from typing import Generic, TypeVar, Type, get_type_hints

E = TypeVar('E')  # Entity
D = TypeVar('D')  # DTO




class BaseDTOMapper(Generic[E, D]):
    """
    Maps between:
    - Domain Entity (pure Python)
    - DTO (Pydantic model)
    """

    ALIAS: dict[str, str] = {}

    def __init__(self, entity_cls: Type[E], dto_cls: Type[D]) -> None:
        self.entity_cls = entity_cls
        self.dto_cls = dto_cls

        self._entity_fields = set(get_type_hints(entity_cls).keys())
        self._dto_fields = set(get_type_hints(dto_cls).keys())

    def to_dto(self, entity: E) -> D:
        """Entity → DTO"""
        dto_data = {}
        for dto_field in self._dto_fields:
            ent_field = self._to_entity_name(dto_field)
            if hasattr(entity, ent_field):
                dto_data[dto_field] = getattr(entity, ent_field)
            else:
                logger.warning(f"[DTOMapper] Field {ent_field} missing in entity {self.entity_cls.__name__}")
        return self.dto_cls(**dto_data)


    def from_dto(self, dto: D) -> E:
        """DTO → Entity"""
        ent_data = {}
        for ent_field in self._entity_fields:
            dto_field = self._to_dto_name(ent_field)
            if hasattr(dto, dto_field):
                ent_data[ent_field] = getattr(dto, dto_field)
            else:
                logger.debug(f"[DTOMapper] Field {dto_field} missing in DTO {self.dto_cls.__name__}")
        return self.entity_cls(**ent_data)

    def _to_entity_name(self, dto_name: str) -> str:
        return self.ALIAS.get(dto_name, dto_name)

    def _to_dto_name(self, ent_name: str) -> str:
        for k, v in self.ALIAS.items():
            if v == ent_name:
                return k
        return ent_name
