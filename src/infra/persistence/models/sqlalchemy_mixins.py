from datetime import datetime, timezone  # Ensure timezone is imported

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class SQLAlchemyTIMESTAMPMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc), # Python-side default for new objects
        server_default=func.now() # DB-side default on INSERT
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc), # Python-side default for new objects
        onupdate=lambda: datetime.now(timezone.utc), # Python-side value on UPDATE
        server_default=func.now(), # DB-side default on INSERT
        # server_onupdate=func.now() # For some dialects, use this if you want the DB func on update
                                     # but for PostgreSQL, a trigger is more common for true server-side ON UPDATE
        # *** REMOVE onupdate_server_default ***
    )
