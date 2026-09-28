"""
PostgreSQL async connection management using SQLAlchemy 2.0.

Provides:
- Async engine and session factory.
- Session dependency for FastAPI (via get_postgres_session).
- Startup/shutdown lifecycle hooks.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from core.config import settings


# ── Engine & Session Factory ────────────────────────────

engine = create_async_engine(
    settings.POSTGRES_URL,
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Base Model ──────────────────────────────────────────

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


# ── Lifecycle Hooks ─────────────────────────────────────

async def init_postgres() -> None:
    """Initialize PostgreSQL connection pool."""
    # In production, tables are created via Alembic migrations.
    # This is only for initial development convenience.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_postgres() -> None:
    """Close PostgreSQL connection pool."""
    await engine.dispose()


# ── Session Dependency ──────────────────────────────────

async def get_postgres_session():
    """
    FastAPI dependency that provides a database session.

    Usage:
        @router.get("/")
        async def endpoint(db: AsyncSession = Depends(get_postgres_session)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
