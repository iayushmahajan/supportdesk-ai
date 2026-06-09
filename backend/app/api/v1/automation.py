import uuid

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.schemas.automation import (
    AutomationCallbackRequest,
    AutomationWebhookTestRequest,
)
from app.services.automation_service import (
    record_automation_callback,
    trigger_ai_completed_automation,
    trigger_ticket_created_automation,
)
from app.services.ticket_service import get_ticket_or_404

router = APIRouter(prefix="/automation", tags=["Automation"])


@router.post("/webhook-test")
def webhook_test_endpoint(payload: AutomationWebhookTestRequest):
    return {
        "status": "ok",
        "message": payload.message,
    }


@router.post("/ticket-created/{ticket_id}")
def trigger_ticket_created_endpoint(
    ticket_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    ticket = get_ticket_or_404(session=session, ticket_id=ticket_id)
    event = trigger_ticket_created_automation(session=session, ticket=ticket)

    return {
        "status": event.status,
        "event_type": event.event_type,
        "event_id": str(event.id),
    }


@router.post("/ai-completed/{ticket_id}")
def trigger_ai_completed_endpoint(
    ticket_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    ticket = get_ticket_or_404(session=session, ticket_id=ticket_id)
    event = trigger_ai_completed_automation(session=session, ticket=ticket)

    return {
        "status": event.status,
        "event_type": event.event_type,
        "event_id": str(event.id),
    }


@router.post("/callback")
def automation_callback_endpoint(
    callback_data: AutomationCallbackRequest,
    session: Session = Depends(get_session),
):
    ticket = get_ticket_or_404(session=session, ticket_id=callback_data.ticket_id)
    event = record_automation_callback(
        session=session,
        ticket=ticket,
        callback_data=callback_data,
    )

    return {
        "status": event.status,
        "event_type": event.event_type,
        "event_id": str(event.id),
    }