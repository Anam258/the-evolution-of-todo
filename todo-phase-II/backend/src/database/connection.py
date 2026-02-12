"""
Database connection management for Neon Serverless PostgreSQL.

Provides SQLAlchemy engine with serverless-optimized connection pooling
and session management for FastAPI dependency injection.
"""

from sqlmodel import Session, SQLModel, create_engine
from typing import Generator

from config.settings import settings


# Validate DATABASE_URL is set
if not settings.database_url:
    raise ValueError(
        "DATABASE_URL environment variable not set. "
        "Please create a .env file with DATABASE_URL or set it in your environment. "
        "See .env.example for template."
    )

# Create engine with Neon Serverless PostgreSQL optimized settings
engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # Log SQL queries in development
    pool_pre_ping=True,  # Verify connection health before use
    pool_size=5,  # Small pool for serverless (Neon has connection limits)
    max_overflow=10,  # Allow burst connections under load
    pool_timeout=30,  # Wait up to 30 seconds for available connection
    pool_recycle=3600,  # Recycle connections after 1 hour (Neon best practice)
)


def init_db() -> None:
    """
    Initialize database schema by creating all tables.

    This function creates all tables defined in SQLModel models.
    For development/testing only - use Alembic migrations in production.

    Usage:
        from src.database.connection import init_db
        init_db()
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to inject database sessions.

    Yields a SQLModel Session that is automatically closed after use.
    Use with FastAPI's Depends() for automatic session management.

    Usage in FastAPI route:
        @app.get("/items")
        def get_items(session: Session = Depends(get_session)):
            items = session.exec(select(Item)).all()
            return items

    Yields:
        Session: SQLModel database session
    """
    with Session(engine) as session:
        yield session
