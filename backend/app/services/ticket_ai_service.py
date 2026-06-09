import logging
from datetime import datetime
from typing import Any

from pydantic import ValidationError
from sqlmodel import Session

from app.core.config import get_settings
from app.models.ticket import (
    AgentRun,
    AgentRunStatus,
    GeneratedResponse,
    Ticket,
    TicketCategory,
    TicketPriority,
)
from app.schemas.ai import TicketAIResult
from app.services.llm_service import LLMServiceError, call_openai_compatible_chat_completion

logger = logging.getLogger(__name__)

settings = get_settings()


def _build_system_prompt() -> str:
    return """
You are an AI support ticket triage assistant.

You must analyze a support ticket and return ONLY valid JSON.

Required JSON shape:
{
  "category": "technical | billing | account | document | general",
  "priority": "low | medium | high | urgent",
  "suggested_department": "string",
  "extracted_entities": {
    "key": "value"
  },
  "missing_information": ["string"],
  "internal_summary": "string",
  "response_draft": "string"
}

Rules:
- category must be one of: technical, billing, account, document, general
- priority must be one of: low, medium, high, urgent
- suggested_department should be realistic, for example IT Support, Billing, Customer Operations, Document Processing
- missing_information should list details needed to resolve the ticket
- response_draft should be a professional reply to the requester
- Do not include markdown
- Do not include extra text outside JSON
""".strip()


def _build_user_prompt(ticket: Ticket) -> str:
    return f"""
Analyze this support ticket.

Requester name:
{ticket.requester_name}

Requester email:
{ticket.requester_email}

Subject:
{ticket.subject}

Description:
{ticket.description}

Source:
{ticket.source}
""".strip()


def _fallback_process_ticket(ticket: Ticket) -> TicketAIResult:
    """
    Deterministic fallback processor.

    This keeps local development, tests, and demos working without an API key.
    It also shows recruiters that the backend handles AI failure gracefully.
    """
    text = f"{ticket.subject} {ticket.description}".lower()

    category = TicketCategory.GENERAL
    priority = TicketPriority.MEDIUM
    suggested_department = "Customer Operations"
    missing_information = ["Preferred contact time", "Any relevant screenshots or reference numbers"]

    if any(keyword in text for keyword in ["login", "dashboard", "password", "loading", "error", "bug"]):
        category = TicketCategory.TECHNICAL
        suggested_department = "IT Support"
        missing_information = [
            "Browser and device information",
            "Screenshot of the error or loading state",
            "Approximate time when the issue started",
        ]

    if any(keyword in text for keyword in ["invoice", "billing", "payment", "refund", "discount"]):
        category = TicketCategory.BILLING
        suggested_department = "Billing Support"
        missing_information = [
            "Invoice number",
            "Billing period",
            "Expected amount or discount information",
        ]

    if any(keyword in text for keyword in ["address", "profile", "account", "email"]):
        category = TicketCategory.ACCOUNT
        suggested_department = "Account Support"
        missing_information = [
            "Current account identifier",
            "New details that should be updated",
        ]

    if any(keyword in text for keyword in ["attached", "document", "documents", "file", "processed"]):
        category = TicketCategory.DOCUMENT
        suggested_department = "Document Processing"
        missing_information = [
            "Document type",
            "Processing deadline",
            "Confirmation that all required documents were attached",
        ]

    if any(keyword in text for keyword in ["urgent", "blocked", "cannot work", "production", "critical"]):
        priority = TicketPriority.HIGH

    if any(keyword in text for keyword in ["security", "data loss", "breach", "system down"]):
        priority = TicketPriority.URGENT

    internal_summary = (
        f"{ticket.requester_name} reported: {ticket.subject}. "
        f"The request appears to be a {category.value} issue and should be handled by "
        f"{suggested_department}."
    )

    response_draft = (
        f"Hello {ticket.requester_name},\n\n"
        f"Thank you for contacting support. We received your request about "
        f"\"{ticket.subject}\" and have routed it to {suggested_department}. "
        "To help us resolve this faster, please provide any missing details listed by our support team.\n\n"
        "Best regards,\n"
        "SupportDesk AI Team"
    )

    return TicketAIResult(
        category=category,
        priority=priority,
        suggested_department=suggested_department,
        extracted_entities={
            "requester_name": ticket.requester_name,
            "requester_email": ticket.requester_email,
            "source": ticket.source.value,
            "subject": ticket.subject,
        },
        missing_information=missing_information,
        internal_summary=internal_summary,
        response_draft=response_draft,
    )


def generate_ticket_ai_result(ticket: Ticket) -> TicketAIResult:
    """
    Main AI generation entry point.

    Uses the real LLM if configured.
    Falls back to deterministic processing if the LLM is missing or fails.
    """
    if not settings.has_llm_api_key:
        logger.info("LLM_API_KEY missing. Using fallback AI processor.")
        return _fallback_process_ticket(ticket)

    try:
        raw_result = call_openai_compatible_chat_completion(
            system_prompt=_build_system_prompt(),
            user_prompt=_build_user_prompt(ticket),
        )

        return TicketAIResult.model_validate(raw_result)
    except (LLMServiceError, ValidationError) as exc:
        logger.exception("AI processing failed for ticket_id=%s", ticket.id)

        if not settings.enable_llm_fallback:
            raise

        logger.info("Using fallback AI processor after LLM failure")
        return _fallback_process_ticket(ticket)


def process_ticket_with_ai(session: Session, ticket: Ticket) -> Ticket:
    """
    Processes one ticket with the Phase 4 combined AI workflow.

    Stores:
    - one agent_run record
    - updated ticket category/priority/department/summary
    - one generated response draft
    """
    started_at = datetime.utcnow()

    agent_run = AgentRun(
        ticket_id=ticket.id,
        agent_name="Phase 4 Combined Ticket Processor",
        execution_order=1,
        status=AgentRunStatus.RUNNING,
        input_json={
            "ticket_id": str(ticket.id),
            "subject": ticket.subject,
            "description": ticket.description,
            "source": ticket.source.value,
        },
        started_at=started_at,
    )

    session.add(agent_run)
    session.commit()
    session.refresh(agent_run)

    try:
        ai_result = generate_ticket_ai_result(ticket)

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

        agent_run.status = AgentRunStatus.COMPLETED
        agent_run.output_json = ai_result.model_dump(mode="json")
        agent_run.completed_at = datetime.utcnow()

        session.add(ticket)
        session.add(generated_response)
        session.add(agent_run)
        session.commit()
        session.refresh(ticket)

        logger.info("AI processing completed for ticket_id=%s", ticket.id)

        return ticket

    except Exception as exc:
        agent_run.status = AgentRunStatus.FAILED
        agent_run.error_message = str(exc)
        agent_run.completed_at = datetime.utcnow()

        session.add(agent_run)
        session.commit()

        logger.exception("AI processing failed for ticket_id=%s", ticket.id)
        raise