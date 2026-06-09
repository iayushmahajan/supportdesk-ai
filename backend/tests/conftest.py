import os

import psycopg
import pytest
from sqlalchemy.engine import make_url
from sqlmodel import SQLModel, Session, create_engine, delete

# ---------------------------------------------------------------------
# Test database setup
# ---------------------------------------------------------------------
# IMPORTANT:
# These environment variables are set before importing app.main or
# app.core.database. This ensures tests use supportdesk_ai_test instead
# of the normal development database supportdesk_ai.
# ---------------------------------------------------------------------

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://supportdesk_user:supportdesk_password@localhost:5433/supportdesk_ai_test",
)

os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["ENABLE_DEMO_SEED"] = "false"


def ensure_test_database_exists() -> None:
    """
    Creates the test database if it does not already exist.

    PostgreSQL official Docker image creates only the main database
    automatically. This helper creates supportdesk_ai_test for pytest.
    """
    test_db_url = make_url(TEST_DATABASE_URL)
    test_db_name = test_db_url.database

    if not test_db_name:
        raise RuntimeError("TEST_DATABASE_URL must include a database name")

    # Connect to the normal development database as an admin connection.
    # We only use this connection to create the separate test database.
    admin_url = test_db_url.set(database="supportdesk_ai")
    admin_url_str = admin_url.render_as_string(hide_password=False).replace(
        "postgresql+psycopg://",
        "postgresql://",
    )

    with psycopg.connect(admin_url_str, autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (test_db_name,),
            )
            exists = cursor.fetchone()

            if not exists:
                cursor.execute(f'CREATE DATABASE "{test_db_name}"')


ensure_test_database_exists()

# Imports must happen after DATABASE_URL has been changed to TEST_DATABASE_URL.
from app.core.database import engine  # noqa: E402
from app.models.ticket import (  # noqa: E402
    AgentRun,
    AutomationEvent,
    GeneratedResponse,
    Ticket,
    TicketAttachment,
    TicketMessage,
)
from app.models.user import User  # noqa: E402


@pytest.fixture(autouse=True)
def clean_test_database():
    """
    Keeps tests isolated by clearing only the test database.

    This no longer touches the normal development database.
    """
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        session.exec(delete(AutomationEvent))
        session.exec(delete(GeneratedResponse))
        session.exec(delete(AgentRun))
        session.exec(delete(TicketAttachment))
        session.exec(delete(TicketMessage))
        session.exec(delete(Ticket))
        session.exec(delete(User))
        session.commit()

    yield

    with Session(engine) as session:
        session.exec(delete(AutomationEvent))
        session.exec(delete(GeneratedResponse))
        session.exec(delete(AgentRun))
        session.exec(delete(TicketAttachment))
        session.exec(delete(TicketMessage))
        session.exec(delete(Ticket))
        session.exec(delete(User))
        session.commit()