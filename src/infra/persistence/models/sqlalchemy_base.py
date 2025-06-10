from sqlalchemy import Column, Integer, UUID
from uuid import uuid4

from sqlalchemy.orm import declarative_base
from src.infra.persistence.models.sqlalchemy_mixins import SQLAlchemyTIMESTAMPMixin
from sqlalchemy.orm import Mapped, mapped_column

Base = declarative_base()

class SQLAlchemyBase(Base, SQLAlchemyTIMESTAMPMixin):
    __abstract__ = True

    uid: Mapped[uuid4] = mapped_column(UUID(as_uuid=True),primary_key=True, unique=True, nullable=False, default=uuid4)

