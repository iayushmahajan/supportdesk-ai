from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def valid_ticket_payload() -> dict[str, str]:
    return {
        "requester_name": "Automation User",
        "requester_email": "automation.user@example.com",
        "subject": "Please update my address",
        "description": "I need to update my billing address.",
        "source": "form",
    }


def test_webhook_test_endpoint() -> None:
    response = client.post(
        "/api/v1/automation/webhook-test",
        json={"message": "Hello n8n"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["message"] == "Hello n8n"


def test_ticket_created_automation_endpoint_records_event() -> None:
    create_response = client.post("/api/v1/tickets", json=valid_ticket_payload())
    assert create_response.status_code == 201

    ticket_id = create_response.json()["id"]

    response = client.post(f"/api/v1/automation/ticket-created/{ticket_id}")

    assert response.status_code == 200
    assert response.json()["status"] == "sent"
    assert response.json()["event_type"] == "ticket_created"


def test_ai_completed_automation_endpoint_records_event() -> None:
    create_response = client.post("/api/v1/tickets", json=valid_ticket_payload())
    assert create_response.status_code == 201

    ticket_id = create_response.json()["id"]

    response = client.post(f"/api/v1/automation/ai-completed/{ticket_id}")

    assert response.status_code == 200
    assert response.json()["status"] == "sent"
    assert response.json()["event_type"] == "ai_completed"


def test_automation_callback_records_event() -> None:
    create_response = client.post("/api/v1/tickets", json=valid_ticket_payload())
    assert create_response.status_code == 201

    ticket_id = create_response.json()["id"]

    response = client.post(
        "/api/v1/automation/callback",
        json={
            "ticket_id": ticket_id,
            "event_type": "n8n_callback_test",
            "status": "sent",
            "provider": "n8n",
            "response_json": {"message": "Callback received"},
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "sent"
    assert response.json()["event_type"] == "n8n_callback_test"