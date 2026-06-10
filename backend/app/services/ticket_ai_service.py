import logging
from datetime import datetime

from sqlmodel import Session

from app.models.ticket import GeneratedResponse, Ticket
from app.schemas.ai import TicketAIResult
from app.services.agent_workflow_service import (
    convert_workflow_result_to_ticket_ai_result,
    run_multi_agent_ticket_workflow,
)

logger = logging.getLogger(__name__)


def generate_ticket_ai_result(ticket: Ticket) -> TicketAIResult:
    """
    Compatibility function used by tests and existing imports.

    This function remains for backwards compatibility and deterministic test mocking.
    """
    raise RuntimeError(
        "generate_ticket_ai_result is no longer used directly. "
        "Use process_ticket_with_ai instead."
    )


def process_ticket_with_ai(session: Session, ticket: Ticket) -> Ticket:
    """
    Processes one ticket with the multi-agent workflow.

    Stores:
    - one agent_run per agent
    - updated ticket category/priority/department/summary
    - one generated response draft
    """
    workflow_result = run_multi_agent_ticket_workflow(
        session=session,
        ticket=ticket,
    )

    ai_result = convert_workflow_result_to_ticket_ai_result(workflow_result)

    ticket.category = ai_result.category
    ticket.priority = ai_result.priority
    ticket.suggested_department = ai_result.suggested_department
    ticket.internal_summary = ai_result.internal_summary
    ticket.updated_at = datetime.utcnow()

    generated_response = GeneratedResponse(
        ticket_id=ticket.id,
        response_text=ai_result.response_draft,
        tone="professional",
        is_approved=False,
    )

    session.add(ticket)
    session.add(generated_response)
    session.commit()
    session.refresh(ticket)

    logger.info("Multi-agent AI processing completed for ticket_id=%s", ticket.id)

    return ticket