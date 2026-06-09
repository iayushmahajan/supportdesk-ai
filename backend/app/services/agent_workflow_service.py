import logging
from datetime import datetime
from typing import Any, Callable

from pydantic import BaseModel, ValidationError
from sqlmodel import Session

from app.core.config import get_settings
from app.models.ticket import AgentRun, AgentRunStatus, Ticket
from app.schemas.agent import (
    ClassificationAgentOutput,
    IntakeAgentOutput,
    MissingInfoAgentOutput,
    MultiAgentWorkflowResult,
    PriorityAgentOutput,
    ResponseDraftAgentOutput,
    RoutingAgentOutput,
    SummaryAgentOutput,
)
from app.schemas.ai import TicketAIResult
from app.services.llm_service import LLMServiceError, call_openai_compatible_chat_completion

logger = logging.getLogger(__name__)
settings = get_settings()


AgentCallable = Callable[[Ticket, dict[str, Any]], BaseModel]


def _create_running_agent_run(
    *,
    session: Session,
    ticket: Ticket,
    agent_name: str,
    execution_order: int,
    input_json: dict[str, Any],
) -> AgentRun:
    agent_run = AgentRun(
        ticket_id=ticket.id,
        agent_name=agent_name,
        execution_order=execution_order,
        status=AgentRunStatus.RUNNING,
        input_json=input_json,
        started_at=datetime.utcnow(),
    )

    session.add(agent_run)
    session.commit()
    session.refresh(agent_run)

    return agent_run


def _complete_agent_run(
    *,
    session: Session,
    agent_run: AgentRun,
    output: BaseModel,
) -> None:
    agent_run.status = AgentRunStatus.COMPLETED
    agent_run.output_json = output.model_dump(mode="json")
    agent_run.completed_at = datetime.utcnow()

    session.add(agent_run)
    session.commit()


def _fail_agent_run(
    *,
    session: Session,
    agent_run: AgentRun,
    error: Exception,
) -> None:
    agent_run.status = AgentRunStatus.FAILED
    agent_run.error_message = str(error)
    agent_run.completed_at = datetime.utcnow()

    session.add(agent_run)
    session.commit()


def _run_agent(
    *,
    session: Session,
    ticket: Ticket,
    agent_name: str,
    execution_order: int,
    context: dict[str, Any],
    agent_function: AgentCallable,
) -> BaseModel:
    agent_run = _create_running_agent_run(
        session=session,
        ticket=ticket,
        agent_name=agent_name,
        execution_order=execution_order,
        input_json={
            "ticket_id": str(ticket.id),
            "subject": ticket.subject,
            "description": ticket.description,
            "context": context,
        },
    )

    try:
        output = agent_function(ticket, context)

        _complete_agent_run(
            session=session,
            agent_run=agent_run,
            output=output,
        )

        logger.info(
            "Agent completed: ticket_id=%s agent=%s",
            ticket.id,
            agent_name,
        )

        return output

    except Exception as exc:
        _fail_agent_run(
            session=session,
            agent_run=agent_run,
            error=exc,
        )

        logger.exception(
            "Agent failed: ticket_id=%s agent=%s",
            ticket.id,
            agent_name,
        )

        raise


def _ticket_text(ticket: Ticket) -> str:
    return f"{ticket.subject} {ticket.description}".lower()


def intake_agent(ticket: Ticket, context: dict[str, Any]) -> IntakeAgentOutput:
    text = _ticket_text(ticket)

    intent = "General support request"

    if any(word in text for word in ["login", "password", "dashboard", "loading", "error"]):
        intent = "Resolve technical access or dashboard issue"
    elif any(word in text for word in ["invoice", "billing", "payment", "discount"]):
        intent = "Resolve billing or invoice issue"
    elif any(word in text for word in ["address", "profile", "account"]):
        intent = "Update account information"
    elif any(word in text for word in ["document", "attached", "file", "processed"]):
        intent = "Process submitted documents"

    return IntakeAgentOutput(
        intent=intent,
        extracted_entities={
            "requester_name": ticket.requester_name,
            "requester_email": ticket.requester_email,
            "subject": ticket.subject,
            "source": ticket.source.value,
        },
    )


def classification_agent(
    ticket: Ticket,
    context: dict[str, Any],
) -> ClassificationAgentOutput:
    text = _ticket_text(ticket)

    category = "general"
    reasoning = "No strong category-specific keywords were detected."

    if any(word in text for word in ["login", "password", "dashboard", "loading", "error", "bug"]):
        category = "technical"
        reasoning = "The ticket describes access, dashboard, loading, or technical behavior."
    elif any(word in text for word in ["invoice", "billing", "payment", "refund", "discount"]):
        category = "billing"
        reasoning = "The ticket mentions invoice, billing, payment, refund, or discount details."
    elif any(word in text for word in ["address", "profile", "account", "email"]):
        category = "account"
        reasoning = "The ticket asks for account or profile information changes."
    elif any(word in text for word in ["attached", "document", "documents", "file", "processed"]):
        category = "document"
        reasoning = "The ticket refers to documents, files, attachments, or processing."

    return ClassificationAgentOutput(
        category=category,
        reasoning=reasoning,
    )


def priority_agent(ticket: Ticket, context: dict[str, Any]) -> PriorityAgentOutput:
    text = _ticket_text(ticket)

    priority = "medium"
    reasoning = "The ticket needs support attention but does not indicate severe impact."

    if any(word in text for word in ["urgent", "blocked", "cannot work", "production", "critical"]):
        priority = "high"
        reasoning = "The ticket suggests the requester is blocked or the issue has high operational impact."

    if any(word in text for word in ["security", "data loss", "breach", "system down"]):
        priority = "urgent"
        reasoning = "The ticket suggests security, data loss, breach, or full system outage risk."

    if any(word in text for word in ["question", "minor", "when possible"]):
        priority = "low"
        reasoning = "The ticket appears non-urgent and can be handled after higher-impact requests."

    return PriorityAgentOutput(
        priority=priority,
        reasoning=reasoning,
    )


def routing_agent(ticket: Ticket, context: dict[str, Any]) -> RoutingAgentOutput:
    category = context.get("category")

    routing_map = {
        "technical": "IT Support",
        "billing": "Billing Support",
        "account": "Account Support",
        "document": "Document Processing",
        "general": "Customer Operations",
    }

    suggested_department = routing_map.get(str(category), "Customer Operations")

    return RoutingAgentOutput(
        suggested_department=suggested_department,
        reasoning=f"The ticket category is {category}, so it should be routed to {suggested_department}.",
    )


def missing_info_agent(
    ticket: Ticket,
    context: dict[str, Any],
) -> MissingInfoAgentOutput:
    category = context.get("category")

    missing_by_category = {
        "technical": [
            "Browser and device information",
            "Screenshot of the error or loading state",
            "Approximate time when the issue started",
        ],
        "billing": [
            "Invoice number",
            "Billing period",
            "Expected amount or discount information",
        ],
        "account": [
            "Current account identifier",
            "New details that should be updated",
        ],
        "document": [
            "Document type",
            "Processing deadline",
            "Confirmation that all required documents were attached",
        ],
        "general": [
            "Preferred contact time",
            "Any relevant reference number",
        ],
    }

    return MissingInfoAgentOutput(
        missing_information=missing_by_category.get(str(category), missing_by_category["general"]),
    )


def summary_agent(ticket: Ticket, context: dict[str, Any]) -> SummaryAgentOutput:
    category = context.get("category", "general")
    priority = context.get("priority", "medium")
    department = context.get("suggested_department", "Customer Operations")
    intent = context.get("intent", "support request")

    return SummaryAgentOutput(
        internal_summary=(
            f"{ticket.requester_name} submitted a {category} ticket about "
            f"'{ticket.subject}'. The detected intent is: {intent}. "
            f"The priority is {priority}, and the ticket should be handled by {department}."
        )
    )


def response_draft_agent(
    ticket: Ticket,
    context: dict[str, Any],
) -> ResponseDraftAgentOutput:
    department = context.get("suggested_department", "Customer Operations")
    missing_information = context.get("missing_information", [])

    missing_text = ""
    if missing_information:
        missing_text = (
            "\n\nTo help us resolve this faster, please share the following details:\n"
            + "\n".join(f"- {item}" for item in missing_information)
        )

    return ResponseDraftAgentOutput(
        response_draft=(
            f"Hello {ticket.requester_name},\n\n"
            f"Thank you for contacting support. We received your request about "
            f"\"{ticket.subject}\" and routed it to {department}."
            f"{missing_text}\n\n"
            "Best regards,\n"
            "SupportDesk AI Team"
        )
    )


def _build_llm_system_prompt(agent_name: str) -> str:
    return f"""
You are the {agent_name} in a support ticket triage workflow.
Return ONLY valid JSON.
Do not include markdown.
Do not include extra text.
""".strip()


def _call_llm_agent(
    *,
    ticket: Ticket,
    context: dict[str, Any],
    agent_name: str,
    expected_schema: type[BaseModel],
    instruction: str,
) -> BaseModel:
    user_prompt = f"""
Ticket:
Requester: {ticket.requester_name} <{ticket.requester_email}>
Subject: {ticket.subject}
Description: {ticket.description}
Source: {ticket.source.value}

Existing workflow context:
{context}

Instruction:
{instruction}
""".strip()

    raw_result = call_openai_compatible_chat_completion(
        system_prompt=_build_llm_system_prompt(agent_name),
        user_prompt=user_prompt,
    )

    return expected_schema.model_validate(raw_result)


def llm_or_fallback_agent(
    *,
    ticket: Ticket,
    context: dict[str, Any],
    agent_name: str,
    expected_schema: type[BaseModel],
    instruction: str,
    fallback_function: AgentCallable,
) -> BaseModel:
    if not settings.has_llm_api_key:
        return fallback_function(ticket, context)

    try:
        return _call_llm_agent(
            ticket=ticket,
            context=context,
            agent_name=agent_name,
            expected_schema=expected_schema,
            instruction=instruction,
        )
    except (LLMServiceError, ValidationError) as exc:
        logger.exception("LLM agent failed: %s", agent_name)

        if not settings.enable_llm_fallback:
            raise

        logger.info("Using fallback for agent: %s", agent_name)
        return fallback_function(ticket, context)


def run_multi_agent_ticket_workflow(
    *,
    session: Session,
    ticket: Ticket,
) -> MultiAgentWorkflowResult:
    """
    Runs the Phase 5 multi-agent workflow and stores every step as agent_run.

    Each agent receives the context produced by previous agents.
    """
    context: dict[str, Any] = {}

    intake_output = _run_agent(
        session=session,
        ticket=ticket,
        agent_name="Intake Agent",
        execution_order=1,
        context=context,
        agent_function=lambda current_ticket, current_context: llm_or_fallback_agent(
            ticket=current_ticket,
            context=current_context,
            agent_name="Intake Agent",
            expected_schema=IntakeAgentOutput,
            instruction=(
                "Extract the request intent and key entities. "
                "Return JSON with intent and extracted_entities."
            ),
            fallback_function=intake_agent,
        ),
    )
    context.update(intake_output.model_dump(mode="json"))

    classification_output = _run_agent(
        session=session,
        ticket=ticket,
        agent_name="Classification Agent",
        execution_order=2,
        context=context,
        agent_function=lambda current_ticket, current_context: llm_or_fallback_agent(
            ticket=current_ticket,
            context=current_context,
            agent_name="Classification Agent",
            expected_schema=ClassificationAgentOutput,
            instruction=(
                "Classify the ticket category. "
                "Return JSON with category and reasoning. "
                "Allowed categories: technical, billing, account, document, general."
            ),
            fallback_function=classification_agent,
        ),
    )
    context.update(classification_output.model_dump(mode="json"))

    priority_output = _run_agent(
        session=session,
        ticket=ticket,
        agent_name="Priority Agent",
        execution_order=3,
        context=context,
        agent_function=lambda current_ticket, current_context: llm_or_fallback_agent(
            ticket=current_ticket,
            context=current_context,
            agent_name="Priority Agent",
            expected_schema=PriorityAgentOutput,
            instruction=(
                "Determine ticket priority. "
                "Return JSON with priority and reasoning. "
                "Allowed priorities: low, medium, high, urgent."
            ),
            fallback_function=priority_agent,
        ),
    )
    context.update(priority_output.model_dump(mode="json"))

    routing_output = _run_agent(
        session=session,
        ticket=ticket,
        agent_name="Routing Agent",
        execution_order=4,
        context=context,
        agent_function=lambda current_ticket, current_context: llm_or_fallback_agent(
            ticket=current_ticket,
            context=current_context,
            agent_name="Routing Agent",
            expected_schema=RoutingAgentOutput,
            instruction=(
                "Suggest the best support department/team. "
                "Return JSON with suggested_department and reasoning."
            ),
            fallback_function=routing_agent,
        ),
    )
    context.update(routing_output.model_dump(mode="json"))

    missing_info_output = _run_agent(
        session=session,
        ticket=ticket,
        agent_name="Missing Information Agent",
        execution_order=5,
        context=context,
        agent_function=lambda current_ticket, current_context: llm_or_fallback_agent(
            ticket=current_ticket,
            context=current_context,
            agent_name="Missing Information Agent",
            expected_schema=MissingInfoAgentOutput,
            instruction=(
                "Identify missing information needed to resolve the ticket. "
                "Return JSON with missing_information as a list of strings."
            ),
            fallback_function=missing_info_agent,
        ),
    )
    context.update(missing_info_output.model_dump(mode="json"))

    summary_output = _run_agent(
        session=session,
        ticket=ticket,
        agent_name="Summary Agent",
        execution_order=6,
        context=context,
        agent_function=lambda current_ticket, current_context: llm_or_fallback_agent(
            ticket=current_ticket,
            context=current_context,
            agent_name="Summary Agent",
            expected_schema=SummaryAgentOutput,
            instruction=(
                "Write a concise internal summary for a support agent. "
                "Return JSON with internal_summary."
            ),
            fallback_function=summary_agent,
        ),
    )
    context.update(summary_output.model_dump(mode="json"))

    response_output = _run_agent(
        session=session,
        ticket=ticket,
        agent_name="Response Draft Agent",
        execution_order=7,
        context=context,
        agent_function=lambda current_ticket, current_context: llm_or_fallback_agent(
            ticket=current_ticket,
            context=current_context,
            agent_name="Response Draft Agent",
            expected_schema=ResponseDraftAgentOutput,
            instruction=(
                "Write a professional response draft to the requester. "
                "Return JSON with response_draft."
            ),
            fallback_function=response_draft_agent,
        ),
    )
    context.update(response_output.model_dump(mode="json"))

    return MultiAgentWorkflowResult(
        category=classification_output.category,
        priority=priority_output.priority,
        suggested_department=routing_output.suggested_department,
        extracted_entities=intake_output.extracted_entities,
        missing_information=missing_info_output.missing_information,
        internal_summary=summary_output.internal_summary,
        response_draft=response_output.response_draft,
    )


def convert_workflow_result_to_ticket_ai_result(
    workflow_result: MultiAgentWorkflowResult,
) -> TicketAIResult:
    """
    Keeps compatibility with the Phase 4 TicketAIResult shape.
    """
    return TicketAIResult(
        category=workflow_result.category,
        priority=workflow_result.priority,
        suggested_department=workflow_result.suggested_department,
        extracted_entities=workflow_result.extracted_entities,
        missing_information=workflow_result.missing_information,
        internal_summary=workflow_result.internal_summary,
        response_draft=workflow_result.response_draft,
    )