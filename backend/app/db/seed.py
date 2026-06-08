import logging

from sqlmodel import Session, select

from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate
from app.services.ticket_service import create_new_ticket

logger = logging.getLogger(__name__)


DEMO_TICKETS = [
    TicketCreate(
        requester_name="Maya Schneider",
        requester_email="maya.schneider@example.com",
        subject="Cannot log in to dashboard",
        description=(
            "I cannot log in to the dashboard since this morning. "
            "The page keeps loading after I enter my password."
        ),
        source="form",
    ),
    TicketCreate(
        requester_name="Jonas Weber",
        requester_email="jonas.weber@example.com",
        subject="Invoice amount looks incorrect",
        description=(
            "The invoice for this month looks higher than expected. "
            "Can someone check whether the discount was applied?"
        ),
        source="email",
    ),
    TicketCreate(
        requester_name="Sara Klein",
        requester_email="sara.klein@example.com",
        subject="Please update my billing address",
        description=(
            "We moved offices last week. Please update the billing address "
            "for future invoices."
        ),
        source="form",
    ),
]


def seed_demo_data(session: Session) -> None:
    """
    Adds a few demo tickets only if the table is empty.
    """
    existing_ticket = session.exec(select(Ticket)).first()

    if existing_ticket:
        logger.info("Demo seed skipped because tickets already exist")
        return

    logger.info("Seeding demo tickets")

    for ticket_data in DEMO_TICKETS:
        create_new_ticket(session=session, ticket_data=ticket_data)

    logger.info("Demo tickets seeded successfully")