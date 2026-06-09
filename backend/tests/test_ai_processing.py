from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def valid_ticket_payload() -> dict[str, str]:
    return {
        "requester_name": "AI Test User",
        "requester_email": "ai.test@example.com",
        "subject": "Dashboard is not loading",
        "description": "The dashboard keeps loading after login and I cannot access reports.",
        "source": "form",
    }


def test_process_ai_updates_ticket_with_multi_agent_result() -> None:
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

    assert len(data["agent_runs"]) == 7

    agent_names = [agent_run["agent_name"] for agent_run in data["agent_runs"]]

    assert agent_names == [
        "Intake Agent",
        "Classification Agent",
        "Priority Agent",
        "Routing Agent",
        "Missing Information Agent",
        "Summary Agent",
        "Response Draft Agent",
    ]

    for agent_run in data["agent_runs"]:
        assert agent_run["status"] == "completed"
        assert agent_run["started_at"] is not None
        assert agent_run["completed_at"] is not None
        assert agent_run["output_json"] is not None

    assert len(data["generated_responses"]) == 1
    assert "Hello AI Test User" in data["generated_responses"][0]["response_text"]


def test_process_ai_returns_404_for_unknown_ticket() -> None:
    response = client.post(
        "/api/v1/tickets/11111111-1111-1111-1111-111111111111/process-ai"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_process_ai_for_billing_ticket_sets_billing_category() -> None:
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

    assert len(data["agent_runs"]) == 7
    assert len(data["generated_responses"]) == 1
    assert data["generated_responses"][0]["is_approved"] is False
    assert "Billing Support" in data["generated_responses"][0]["response_text"]


def test_process_ai_rejects_duplicate_processing() -> None:
    create_response = client.post("/api/v1/tickets", json=valid_ticket_payload())

    assert create_response.status_code == 201

    ticket_id = create_response.json()["id"]

    first_response = client.post(f"/api/v1/tickets/{ticket_id}/process-ai")
    second_response = client.post(f"/api/v1/tickets/{ticket_id}/process-ai")

    assert first_response.status_code == 200
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Ticket has already been processed by AI"