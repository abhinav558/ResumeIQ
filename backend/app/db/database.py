"""
ResumeIQ - Database Configuration.

Provides the SQLAlchemy engine, session factory, declarative base,
and database initialization for the persistent application data layer.
"""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# ============================================================================
# DATABASE LOCATION
# ============================================================================

BACKEND_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = BACKEND_ROOT / "resumeiq.db"

DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"


# ============================================================================
# SQLALCHEMY ENGINE
# ============================================================================

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
)


# ============================================================================
# SESSION FACTORY
# ============================================================================

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# ============================================================================
# DECLARATIVE BASE
# ============================================================================

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db() -> None:
    """
    Create all registered database tables if they do not already exist.
    """

    # Import models here so SQLAlchemy registers their tables
    # before create_all() is called.
    from app.models.resume import Resume  # noqa: F401
    from app.models.user import User  # noqa: F401

    Base.metadata.create_all(bind=engine)


# ============================================================================
# DATABASE DEPENDENCY
# ============================================================================

def get_db():
    """
    Provide a database session for a request.

    The session is always closed after the request completes.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()