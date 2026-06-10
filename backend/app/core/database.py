from collections.abc import Generator

from sqlalchemy import text
from sqlmodel import SQLModel, Session, create_engine

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
    """
    with Session(engine) as session:
        yield session


def create_db_and_tables() -> None:
    """
    Creates database tables for local development.

    """
    # Import models before create_all so SQLModel knows them.
    from app.models.ticket import (  # noqa: F401
        AgentRun,
        AutomationEvent,
        GeneratedResponse,
        Ticket,
        TicketAttachment,
        TicketMessage,
    )
    from app.models.user import User  # noqa: F401

    SQLModel.metadata.create_all(engine)


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