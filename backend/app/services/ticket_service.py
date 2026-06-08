import logging
import uuid

from fastapi import HTTPException, status
from sqlmodel import Session

from app.crud.ticket_crud import (
    create_ticket,
    get_ticket_by_id,
    list_tickets,
    update_ticket_status,
)
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate, TicketStatusUpdate

logger = logging.getLogger(__name__)


def create_new_ticket(session: Session, ticket_data: TicketCreate) -> Ticket:
    logger.info("Creating ticket with subject=%s", ticket_data.subject)
    return create_ticket(session=session, ticket_data=ticket_data)


def get_all_tickets(session: Session) -> list[Ticket]:
    logger.info("Listing tickets")
    return list_tickets(session=session)


def get_ticket_or_404(session: Session, ticket_id: uuid.UUID) -> Ticket:
    ticket = get_ticket_by_id(session=session, ticket_id=ticket_id)

    if ticket is None:
        logger.warning("Ticket not found: ticket_id=%s", ticket_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    return ticket


def change_ticket_status(
    session: Session,
    ticket_id: uuid.UUID,
    status_data: TicketStatusUpdate,
) -> Ticket:
    ticket = get_ticket_or_404(session=session, ticket_id=ticket_id)

    logger.info(
        "Updating ticket status: ticket_id=%s old_status=%s new_status=%s",
        ticket.id,
        ticket.status,
        status_data.status,
    )

    return update_ticket_status(
        session=session,
        ticket=ticket,
        status=status_data.status,
    )