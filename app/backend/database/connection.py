from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path

def get_database_url():
    """
    Get database URL from environment variables.

    Supports PostgreSQL configuration via environment variables:
    - DATABASE_URL: Full database URL (takes precedence)
    - POSTGRES_HOST: PostgreSQL host (default: localhost)
    - POSTGRES_PORT: PostgreSQL port (default: 5432)
    - POSTGRES_DB: Database name (default: ai_hedge_fund)
    - POSTGRES_USER: Database user (default: postgres)
    - POSTGRES_PASSWORD: Database password (required for PostgreSQL)

    Returns:
        str: Database URL for SQLAlchemy
    """
    # Check if full DATABASE_URL is provided
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        # Handle postgres:// vs postgresql:// (some services use postgres://)
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        return database_url

    # Build PostgreSQL URL from individual components
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    database = os.environ.get("POSTGRES_DB", "ai_hedge_fund")
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD")

    if not password:
        raise ValueError(
            "PostgreSQL password is required. Set POSTGRES_PASSWORD environment variable.\n"
            "Example: export POSTGRES_PASSWORD=your_password"
        )

    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


# Database configuration
DATABASE_URL = get_database_url()

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=10,  # Connection pool size
    max_overflow=20,  # Allow overflow connections
    echo=False,  # Set to True for SQL query logging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Print database info (without password)
def print_db_info():
    """Print database connection information (without password)"""
    url = DATABASE_URL
    if "@" in url:
        # Hide password
        parts = url.split("@")
        user_pass = parts[0].split("//")[1]
        if ":" in user_pass:
            user = user_pass.split(":")[0]
            url = url.replace(user_pass, f"{user}:****")
    print(f"🗄️  Database: {url}") 