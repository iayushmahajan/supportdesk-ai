import uuid
from datetime import datetime

from sqlmodel import Session, select

from app.models.ticket import MessageSenderType, Ticket, TicketMessage, TicketStatus
from app.schemas.ticket import TicketCreate


def create_ticket(session: Session, ticket_data: TicketCreate) -> Ticket:
    """
    Creates a ticket and stores the initial requester message.
    """
    ticket = Ticket(
        requester_name=ticket_data.requester_name,
        requester_email=str(ticket_data.requester_email),
        subject=ticket_data.subject,
        description=ticket_data.description,
        source=ticket_data.source,
    )

    session.add(ticket)
    session.flush()

    initial_message = TicketMessage(
        ticket_id=ticket.id,
        sender_type=MessageSenderType.REQUESTER,
        sender_name=ticket.requester_name,
        sender_email=ticket.requester_email,
        body=ticket.description,
    )

    session.add(initial_message)
    session.commit()
    session.refresh(ticket)

    return ticket


def list_tickets(session: Session) -> list[Ticket]:
    """
    Returns tickets ordered by newest first.
    """
    statement = select(Ticket).order_by(Ticket.created_at.desc())
    return list(session.exec(statement).all())


def get_ticket_by_id(session: Session, ticket_id: uuid.UUID) -> Ticket | None:
    return session.get(Ticket, ticket_id)


def update_ticket_status(
    session: Session,
    ticket: Ticket,
    status: TicketStatus,
) -> Ticket:
    ticket.status = status
    ticket.updated_at = datetime.utcnow()

    session.add(ticket)
    session.commit()
    session.refresh(ticket)

    return ticket