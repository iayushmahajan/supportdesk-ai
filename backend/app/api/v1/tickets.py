import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.config import get_settings
from app.core.database import get_session
from app.models.ticket import TicketSource
from app.schemas.ticket import (
    EmailTicketCreate,
    TicketCreate,
    TicketDetailRead,
    TicketRead,
    TicketStatusUpdate,
)
from app.services.automation_service import (
    trigger_ai_completed_automation,
    trigger_ticket_created_automation,
)
from app.services.ticket_ai_service import process_ticket_with_ai
from app.services.ticket_service import (
    change_ticket_status,
    create_new_ticket,
    get_all_tickets,
    get_ticket_or_404,
)

router = APIRouter(prefix="/tickets", tags=["Tickets"])
settings = get_settings()


def _ticket_has_ai_result(ticket) -> bool:
    return bool(
        ticket.internal_summary
        or ticket.suggested_department
        or ticket.agent_runs
        or ticket.generated_responses
        or ticket.category != "unclassified"
        or ticket.priority != "unassigned"
    )


def _auto_process_ticket_if_enabled(
    *,
    session: Session,
    ticket_id: uuid.UUID,
):
    """
    Automatically run AI processing after ticket creation.

    We re-fetch the ticket after the ticket-created automation event because
    automation event creation commits the session and refreshes relationships.
    """
    if not settings.enable_auto_ai_processing:
        return get_ticket_or_404(session=session, ticket_id=ticket_id)

    ticket = get_ticket_or_404(session=session, ticket_id=ticket_id)

    if _ticket_has_ai_result(ticket):
        return ticket

    processed_ticket = process_ticket_with_ai(session=session, ticket=ticket)
    trigger_ai_completed_automation(session=session, ticket=processed_ticket)

    return get_ticket_or_404(session=session, ticket_id=ticket_id)


@router.post(
    "",
    response_model=TicketRead,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket_endpoint(
    ticket_data: TicketCreate,
    session: Session = Depends(get_session),
):
    ticket = create_new_ticket(session=session, ticket_data=ticket_data)
    trigger_ticket_created_automation(session=session, ticket=ticket)

    processed_or_original_ticket = _auto_process_ticket_if_enabled(
        session=session,
        ticket_id=ticket.id,
    )

    return processed_or_original_ticket


@router.post(
    "/email-intake",
    response_model=TicketDetailRead,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket_from_email_endpoint(
    email_data: EmailTicketCreate,
    session: Session = Depends(get_session),
):
    ticket_data = TicketCreate(
        requester_name=email_data.from_name,
        requester_email=email_data.from_email,
        subject=email_data.email_subject,
        description=email_data.email_body,
        source=TicketSource.EMAIL,
    )

    ticket = create_new_ticket(session=session, ticket_data=ticket_data)
    trigger_ticket_created_automation(session=session, ticket=ticket)

    _auto_process_ticket_if_enabled(
        session=session,
        ticket_id=ticket.id,
    )

    return get_ticket_or_404(session=session, ticket_id=ticket.id)


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


@router.post("/{ticket_id}/process-ai", response_model=TicketDetailRead)
def process_ticket_ai_endpoint(
    ticket_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    ticket = get_ticket_or_404(session=session, ticket_id=ticket_id)

    if _ticket_has_ai_result(ticket):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ticket has already been processed by AI. Use the reprocess endpoint instead.",
        )

    processed_ticket = process_ticket_with_ai(session=session, ticket=ticket)
    trigger_ai_completed_automation(session=session, ticket=processed_ticket)

    return get_ticket_or_404(session=session, ticket_id=ticket_id)


@router.post("/{ticket_id}/reprocess-ai", response_model=TicketDetailRead)
def reprocess_ticket_ai_endpoint(
    ticket_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    """
    Run AI processing again even if the ticket already has AI output.

    This keeps previous agent runs as history and appends a new workflow run.
    """
    ticket = get_ticket_or_404(session=session, ticket_id=ticket_id)

    processed_ticket = process_ticket_with_ai(session=session, ticket=ticket)
    trigger_ai_completed_automation(session=session, ticket=processed_ticket)

    return get_ticket_or_404(session=session, ticket_id=ticket_id)