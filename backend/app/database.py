"""
Database configuration and session management.
Sets up SQLAlchemy engine and session factory.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=settings.DATABASE_POOL_PRE_PING,
    pool_recycle=settings.DATABASE_POOL_RECYCLE,
    connect_args={
        "check_same_thread": False if "sqlite" in settings.DATABASE_URL else True
    } if "sqlite" in settings.DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session in API routes.
    Usage: def my_route(db: Session = Depends(get_db)):
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database session outside of API routes.
    Usage: with get_db_context() as db:
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"Database context error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


async def init_db() -> None:
    """Initialize database (create tables)."""
    from app.models.base import Base
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")


async def close_db() -> None:
    """Close database connection."""
    engine.dispose()
    logger.info("Database connection closed")


# SQLite-specific configuration for testing
if "sqlite" in settings.DATABASE_URL.lower():
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        """Enable foreign keys for SQLite."""
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
