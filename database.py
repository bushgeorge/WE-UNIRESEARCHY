"""
Database configuration and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os

# Database URL - using SQLite for simplicity
SQLALCHEMY_DATABASE_URL = "sqlite:///./database/research.db"

# Create engine with SQLite specific configuration
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session
    Yields a SQLAlchemy session and ensures it's closed after use
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize database and create tables
    Also seed with initial data if needed
    """
    # Create database directory if it doesn't exist
    os.makedirs("database", exist_ok=True)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Database initialized successfully")