from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def technical_ticket_payload() -> dict[str, str]:
    return {
        "requester_name": "Auto AI User",
        "requester_email": "auto.ai@example.com",
        "subject": "Dashboard is not loading",
        "description": "I cannot open the dashboard after login. It keeps loading.",
        "source": "form",
    }


def test_reprocess_ai_endpoint_adds_another_agent_workflow() -> None:
    create_response = client.post("/api/v1/tickets", json=technical_ticket_payload())
    assert create_response.status_code == 201

    ticket_id = create_response.json()["id"]

    first_process_response = client.post(f"/api/v1/tickets/{ticket_id}/process-ai")
    assert first_process_response.status_code == 200

    first_data = first_process_response.json()
    first_agent_run_count = len(first_data["agent_runs"])

    assert first_agent_run_count == 7

    reprocess_response = client.post(f"/api/v1/tickets/{ticket_id}/reprocess-ai")
    assert reprocess_response.status_code == 200

    reprocessed_data = reprocess_response.json()

    assert reprocessed_data["category"] == "technical"
    assert reprocessed_data["priority"] == "medium"
    assert len(reprocessed_data["agent_runs"]) == 14
    assert len(reprocessed_data["generated_responses"]) == 2
    assert len(reprocessed_data["automation_events"]) >= 2


def test_process_ai_still_rejects_duplicate_processing() -> None:
    create_response = client.post("/api/v1/tickets", json=technical_ticket_payload())
    assert create_response.status_code == 201

    ticket_id = create_response.json()["id"]

    first_process_response = client.post(f"/api/v1/tickets/{ticket_id}/process-ai")
    assert first_process_response.status_code == 200

    duplicate_response = client.post(f"/api/v1/tickets/{ticket_id}/process-ai")

    assert duplicate_response.status_code == 409
    assert "reprocess endpoint" in duplicate_response.json()["detail"]