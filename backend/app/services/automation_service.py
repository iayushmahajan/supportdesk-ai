import logging
from datetime import datetime
from typing import Any

import httpx
from sqlmodel import Session

from app.core.config import get_settings
from app.models.ticket import AutomationEvent, AutomationEventStatus, Ticket
from app.schemas.automation import AutomationCallbackRequest

logger = logging.getLogger(__name__)
settings = get_settings()


def create_automation_event(
    *,
    session: Session,
    ticket: Ticket,
    event_type: str,
    status: AutomationEventStatus,
    payload_json: dict[str, Any] | None = None,
    response_json: dict[str, Any] | None = None,
    error_message: str | None = None,
) -> AutomationEvent:
    event = AutomationEvent(
        ticket_id=ticket.id,
        event_type=event_type,
        status=status,
        provider="n8n",
        payload_json=payload_json,
        response_json=response_json,
        error_message=error_message,
        completed_at=datetime.utcnow()
        if status in [AutomationEventStatus.SENT, AutomationEventStatus.FAILED]
        else None,
    )

    session.add(event)
    session.commit()
    session.refresh(event)

    return event


def _ticket_payload(ticket: Ticket, event_type: str) -> dict[str, Any]:
    return {
        "event_type": event_type,
        "ticket": {
            "id": str(ticket.id),
            "requester_name": ticket.requester_name,
            "requester_email": ticket.requester_email,
            "subject": ticket.subject,
            "description": ticket.description,
            "source": ticket.source.value,
            "status": ticket.status.value,
            "priority": ticket.priority.value,
            "category": ticket.category.value,
            "suggested_department": ticket.suggested_department,
            "internal_summary": ticket.internal_summary,
            "created_at": ticket.created_at.isoformat(),
            "updated_at": ticket.updated_at.isoformat(),
        },
    }


def _post_to_n8n_webhook(
    *,
    webhook_url: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    with httpx.Client(timeout=15) as client:
        response = client.post(webhook_url, json=payload)
        response.raise_for_status()

    if response.content:
        try:
            return response.json()
        except ValueError:
            return {"raw_response": response.text}

    return {"message": "Webhook accepted"}


def trigger_ticket_created_automation(
    *,
    session: Session,
    ticket: Ticket,
) -> AutomationEvent:
    event_type = "ticket_created"
    payload = _ticket_payload(ticket, event_type)

    if not settings.enable_n8n_automation or not settings.has_ticket_created_webhook:
        return create_automation_event(
            session=session,
            ticket=ticket,
            event_type=event_type,
            status=AutomationEventStatus.SENT,
            payload_json=payload,
            response_json={
                "mode": "simulated",
                "message": "Ticket-created automation simulated locally",
            },
        )

    try:
        response_json = _post_to_n8n_webhook(
            webhook_url=settings.n8n_webhook_ticket_created_url or "",
            payload=payload,
        )

        return create_automation_event(
            session=session,
            ticket=ticket,
            event_type=event_type,
            status=AutomationEventStatus.SENT,
            payload_json=payload,
            response_json=response_json,
        )
    except Exception as exc:
        logger.exception("Ticket-created automation failed for ticket_id=%s", ticket.id)

        return create_automation_event(
            session=session,
            ticket=ticket,
            event_type=event_type,
            status=AutomationEventStatus.FAILED,
            payload_json=payload,
            error_message=str(exc),
        )


def trigger_ai_completed_automation(
    *,
    session: Session,
    ticket: Ticket,
) -> AutomationEvent:
    event_type = "ai_completed"
    payload = _ticket_payload(ticket, event_type)

    latest_response = ticket.generated_responses[-1] if ticket.generated_responses else None

    payload["ai_result"] = {
        "category": ticket.category.value,
        "priority": ticket.priority.value,
        "suggested_department": ticket.suggested_department,
        "internal_summary": ticket.internal_summary,
        "latest_response_draft": latest_response.response_text
        if latest_response
        else None,
    }

    if not settings.enable_n8n_automation or not settings.has_ai_completed_webhook:
        return create_automation_event(
            session=session,
            ticket=ticket,
            event_type=event_type,
            status=AutomationEventStatus.SENT,
            payload_json=payload,
            response_json={
                "mode": "simulated",
                "message": "AI-completed automation simulated locally",
            },
        )

    try:
        response_json = _post_to_n8n_webhook(
            webhook_url=settings.n8n_webhook_ai_completed_url or "",
            payload=payload,
        )

        return create_automation_event(
            session=session,
            ticket=ticket,
            event_type=event_type,
            status=AutomationEventStatus.SENT,
            payload_json=payload,
            response_json=response_json,
        )
    except Exception as exc:
        logger.exception("AI-completed automation failed for ticket_id=%s", ticket.id)

        return create_automation_event(
            session=session,
            ticket=ticket,
            event_type=event_type,
            status=AutomationEventStatus.FAILED,
            payload_json=payload,
            error_message=str(exc),
        )


def record_automation_callback(
    *,
    session: Session,
    ticket: Ticket,
    callback_data: AutomationCallbackRequest,
) -> AutomationEvent:
    return create_automation_event(
        session=session,
        ticket=ticket,
        event_type=callback_data.event_type,
        status=callback_data.status,
        payload_json={
            "source": "n8n_callback",
            "ticket_id": str(callback_data.ticket_id),
        },
        response_json=callback_data.response_json,
        error_message=callback_data.error_message,
    )