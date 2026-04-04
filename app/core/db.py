"""
File: app/core/db.py
Purpose: SQLAlchemy database setup.

What this file does:
- Creates the SQLAlchemy engine from DATABASE_URL
- Builds the session factory used per request
- Defines the shared Base class for ORM models
- Exposes `get_db()` so FastAPI routes can safely use DB sessions
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# SQLite needs this special flag because it is stricter about thread usage.
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# The engine is SQLAlchemy's core database connection manager.
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

# SessionLocal is a factory that creates Session objects when needed.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class that ORM models inherit from.
Base = declarative_base()


def get_db():
    # Open one database session for the lifetime of the request.
    db = SessionLocal()
    try:
        # Yield gives control back to FastAPI so the route can use the session.
        yield db
    finally:
        # Always close the session, even if the route raises an error.
        db.close()
