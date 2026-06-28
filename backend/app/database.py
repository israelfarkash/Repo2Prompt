"""Async database engine, session factory, and base model.

Provides SQLAlchemy 2.x async infrastructure using asyncpg as the
PostgreSQL driver. Includes a dependency-injectable session generator
for use with FastAPI's Depends().
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    """SQLAlchemy declarative base class for all ORM models.

    All models should inherit from this class to participate in
    table creation and metadata management.
    """

    pass


async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async database session via dependency injection.

    Yields an AsyncSession that is automatically closed after the
    request completes. Rolls back the transaction on error.

    Yields:
        AsyncSession: An active async database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables() -> None:
    """Create all database tables defined by ORM models.

    Uses the async engine to synchronously execute DDL statements
    via run_sync. Safe to call multiple times; existing tables are
    not recreated.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
