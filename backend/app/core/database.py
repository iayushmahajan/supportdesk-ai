from collections.abc import Generator

from sqlalchemy import text
from sqlmodel import Session, create_engine

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
)


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.
    Later phases will use this for CRUD operations.
    """
    with Session(engine) as session:
        yield session


def check_database_connection() -> bool:
    """
    Simple database health check.

    Runs SELECT 1 against PostgreSQL.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False