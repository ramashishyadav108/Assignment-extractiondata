"""
Database connection and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging
from typing import Generator

from app.config import settings
from .models import Base

logger = logging.getLogger(__name__)

# Create database engine
# For Neon PostgreSQL, use the connection string from settings
if settings.DATABASE_URL:
    # Handle both postgresql:// and postgres:// schemes
    database_url = settings.DATABASE_URL
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    engine = create_engine(
        database_url,
        pool_pre_ping=True,  # Verify connections before using them
        pool_size=10,  # Connection pool size
        max_overflow=20,  # Additional connections that can be created
        echo=settings.DEBUG,  # Log SQL statements in debug mode
    )
    logger.info("Database engine created with Neon PostgreSQL")
else:
    # Fallback to SQLite for local development if no DATABASE_URL
    engine = create_engine(
        "sqlite:///./pdf_extraction.db",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.DEBUG,
    )
    logger.warning("Using SQLite database (DATABASE_URL not configured)")

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database - create all tables.
    
    This should be called on application startup.
    """
    try:
        logger.info("Initializing database...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise


def drop_all_tables() -> None:
    """
    Drop all tables from database.
    
    WARNING: This will delete all data. Use only for development/testing.
    """
    logger.warning("Dropping all tables from database...")
    Base.metadata.drop_all(bind=engine)
    logger.info("All tables dropped")


def reset_db() -> None:
    """
    Reset database by dropping and recreating all tables.
    
    WARNING: This will delete all data. Use only for development/testing.
    """
    drop_all_tables()
    init_db()
    logger.info("Database reset complete")
