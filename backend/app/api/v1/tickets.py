import uuid

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.database import get_session
from app.schemas.ticket import TicketCreate, TicketDetailRead, TicketRead, TicketStatusUpdate
from app.services.ticket_service import (
    change_ticket_status,
    create_new_ticket,
    get_all_tickets,
    get_ticket_or_404,
)

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post(
    "",
    response_model=TicketRead,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket_endpoint(
    ticket_data: TicketCreate,
    session: Session = Depends(get_session),
):
    return create_new_ticket(session=session, ticket_data=ticket_data)


@router.get("", response_model=list[TicketRead])
def list_tickets_endpoint(
    session: Session = Depends(get_session),
):
    return get_all_tickets(session=session)


@router.get("/{ticket_id}", response_model=TicketDetailRead)
def get_ticket_detail_endpoint(
    ticket_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    return get_ticket_or_404(session=session, ticket_id=ticket_id)


@router.patch("/{ticket_id}/status", response_model=TicketRead)
def update_ticket_status_endpoint(
    ticket_id: uuid.UUID,
    status_data: TicketStatusUpdate,
    session: Session = Depends(get_session),
):
    return change_ticket_status(
        session=session,
        ticket_id=ticket_id,
        status_data=status_data,
    )