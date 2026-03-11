"""Database connection and session setup for SQLAlchemy + PostgreSQL."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from sqlalchemy.ext.declarative import declarative_base

# PUBLIC_INTERFACE
def get_database_url():
    """
    Get the database URL from environment variables.
    Expects: POSTGRES_URL, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_PORT (set in .env)
    """
    # Environment variables should be managed via the deployment orchestrator according to provided db_env_vars.
    POSTGRES_URL = os.environ.get("POSTGRES_URL")
    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
    POSTGRES_DB = os.environ.get("POSTGRES_DB")
    POSTGRES_PORT = os.environ.get("POSTGRES_PORT") or "5432"
    if POSTGRES_URL:
        return POSTGRES_URL
    # Compose URL if POSTGRES_URL is not set
    return f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:{POSTGRES_PORT}/{POSTGRES_DB}"

SQLALCHEMY_DATABASE_URL = get_database_url()
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
