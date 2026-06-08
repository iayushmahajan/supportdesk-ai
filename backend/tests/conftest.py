import pytest
from sqlmodel import Session, SQLModel, delete

from app.core.database import engine
from app.models.ticket import (
    AgentRun,
    AutomationEvent,
    GeneratedResponse,
    Ticket,
    TicketAttachment,
    TicketMessage,
)
from app.models.user import User


@pytest.fixture(autouse=True)
def clean_database():
    """
    Keeps tests isolated by clearing all tables before and after each test.

    These tests use the local PostgreSQL database from Docker.
    Make sure docker compose is running before pytest.
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