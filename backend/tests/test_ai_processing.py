from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.models.ticket import TicketCategory, TicketPriority
from app.schemas.ai import TicketAIResult

client = TestClient(app)


def valid_ticket_payload() -> dict[str, str]:
    return {
        "requester_name": "AI Test User",
        "requester_email": "ai.test@example.com",
        "subject": "Dashboard is not loading",
        "description": "The dashboard keeps loading after login and I cannot access reports.",
        "source": "form",
    }


@pytest.fixture
def mock_technical_ai_result(monkeypatch):
    """
    Mock AI processing so tests do not call the real LLM.

    This keeps tests deterministic, fast, and free.
    """

    def fake_generate_ticket_ai_result(ticket):
        return TicketAIResult(
            category=TicketCategory.TECHNICAL,
            priority=TicketPriority.MEDIUM,
            suggested_department="IT Support",
            extracted_entities={
                "requester_name": ticket.requester_name,
                "requester_email": ticket.requester_email,
                "subject": ticket.subject,
                "source": ticket.source.value,
            },
            missing_information=[
                "Browser and device information",
                "Screenshot of the error or loading state",
                "Approximate time when the issue started",
            ],
            internal_summary=(
                f"{ticket.requester_name} reported: {ticket.subject}. "
                "The request appears to be a technical issue and should be handled by IT Support."
            ),
            response_draft=(
                f"Hello {ticket.requester_name},\n\n"
                f"Thank you for contacting support. We received your request about "
                f"\"{ticket.subject}\" and have routed it to IT Support.\n\n"
                "Best regards,\n"
                "SupportDesk AI Team"
            ),
        )

    monkeypatch.setattr(
        "app.services.ticket_ai_service.generate_ticket_ai_result",
        fake_generate_ticket_ai_result,
    )


@pytest.fixture
def mock_billing_ai_result(monkeypatch):
    """
    Mock billing AI output for deterministic billing route test.
    """

    def fake_generate_ticket_ai_result(ticket):
        return TicketAIResult(
            category=TicketCategory.BILLING,
            priority=TicketPriority.MEDIUM,
            suggested_department="Billing Support",
            extracted_entities={
                "requester_name": ticket.requester_name,
                "requester_email": ticket.requester_email,
                "subject": ticket.subject,
                "source": ticket.source.value,
            },
            missing_information=[
                "Invoice number",
                "Billing period",
                "Expected amount or discount information",
            ],
            internal_summary=(
                f"{ticket.requester_name} reported a billing issue about: {ticket.subject}."
            ),
            response_draft=(
                f"Hello {ticket.requester_name},\n\n"
                "Thank you for contacting support. We received your invoice-related request "
                "and routed it to Billing Support.\n\n"
                "Best regards,\n"
                "SupportDesk AI Team"
            ),
        )

    monkeypatch.setattr(
        "app.services.ticket_ai_service.generate_ticket_ai_result",
        fake_generate_ticket_ai_result,
    )


def test_process_ai_updates_ticket_with_mocked_ai_result(
    mock_technical_ai_result,
) -> None:
    create_response = client.post("/api/v1/tickets", json=valid_ticket_payload())

    assert create_response.status_code == 201

    ticket_id = create_response.json()["id"]

    ai_response = client.post(f"/api/v1/tickets/{ticket_id}/process-ai")

    assert ai_response.status_code == 200

    data = ai_response.json()

    assert data["id"] == ticket_id
    assert data["category"] == "technical"
    assert data["priority"] == "medium"
    assert data["suggested_department"] == "IT Support"
    assert data["internal_summary"] is not None

    assert len(data["agent_runs"]) == 1
    assert data["agent_runs"][0]["agent_name"] == "Phase 4 Combined Ticket Processor"
    assert data["agent_runs"][0]["status"] == "completed"
    assert data["agent_runs"][0]["output_json"]["category"] == "technical"
    assert data["agent_runs"][0]["output_json"]["missing_information"] == [
        "Browser and device information",
        "Screenshot of the error or loading state",
        "Approximate time when the issue started",
    ]

    assert len(data["generated_responses"]) == 1
    assert "Hello AI Test User" in data["generated_responses"][0]["response_text"]


def test_process_ai_returns_404_for_unknown_ticket() -> None:
    response = client.post(
        "/api/v1/tickets/11111111-1111-1111-1111-111111111111/process-ai"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_process_ai_for_billing_ticket_sets_billing_category(
    mock_billing_ai_result,
) -> None:
    payload = {
        "requester_name": "Billing User",
        "requester_email": "billing.user@example.com",
        "subject": "Invoice amount looks wrong",
        "description": "My invoice amount is higher than expected and the discount is missing.",
        "source": "email",
    }

    create_response = client.post("/api/v1/tickets", json=payload)

    assert create_response.status_code == 201

    ticket_id = create_response.json()["id"]

    ai_response = client.post(f"/api/v1/tickets/{ticket_id}/process-ai")

    assert ai_response.status_code == 200

    data = ai_response.json()

    assert data["category"] == "billing"
    assert data["priority"] == "medium"
    assert data["suggested_department"] == "Billing Support"

    assert len(data["agent_runs"]) == 1
    assert data["agent_runs"][0]["status"] == "completed"
    assert data["agent_runs"][0]["output_json"]["category"] == "billing"

    assert len(data["generated_responses"]) == 1
    assert data["generated_responses"][0]["is_approved"] is False
    assert "Billing Support" in data["generated_responses"][0]["response_text"]