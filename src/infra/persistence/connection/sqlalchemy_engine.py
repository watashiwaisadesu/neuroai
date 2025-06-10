# src/infra/persistence/connection/sqlalchemy_engine.py
from __future__ import annotations
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine

from src.config import Settings

_settings: Settings = Settings()

async_engine: AsyncEngine = create_async_engine(_settings.ASYNC_DATABASE_URL, echo=False)

# FIX: Use async_sessionmaker for asynchronous sessions
AsyncSessionLocal = async_sessionmaker( # <--- Changed from sessionmaker
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_async_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session