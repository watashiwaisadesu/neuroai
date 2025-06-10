from sqlalchemy import String, Text, TIMESTAMP, Integer
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column
from src.infra.persistence.models.sqlalchemy_base import Base


class LogEntryORM(Base):
    __tablename__ = 'logs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    log_level: Mapped[str | None] = mapped_column(String(10), nullable=False)
    source: Mapped[str | None] = mapped_column(String(255),nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=False)


    # def __repr__(self):
    #     return (f"<LogEntryORM(id={self.id}, timestamp={self.timestamp}, "
    #             f"level={self.log_level}, source='{self.source}', "
    #             f"message='{self.message[:50]}...')>")

