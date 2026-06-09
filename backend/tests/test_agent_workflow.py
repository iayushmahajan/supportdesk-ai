from sqlmodel import Session

from app.core.database import engine
from app.models.ticket import TicketCategory, TicketPriority
from app.schemas.ticket import TicketCreate
from app.services.agent_workflow_service import run_multi_agent_ticket_workflow
from app.services.ticket_service import create_new_ticket


def test_run_multi_agent_ticket_workflow_returns_expected_result() -> None:
    ticket_data = TicketCreate(
        requester_name="Workflow User",
        requester_email="workflow.user@example.com",
        subject="Dashboard is not loading",
        description="The dashboard keeps loading after login.",
        source="form",
    )

    with Session(engine) as session:
        ticket = create_new_ticket(session=session, ticket_data=ticket_data)

        result = run_multi_agent_ticket_workflow(
            session=session,
            ticket=ticket,
        )

        assert result.category == TicketCategory.TECHNICAL
        assert result.priority == TicketPriority.MEDIUM
        assert result.suggested_department == "IT Support"
        assert "Browser and device information" in result.missing_information
        assert result.internal_summary
        assert result.response_draft