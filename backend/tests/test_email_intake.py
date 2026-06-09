from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_email_intake_creates_email_ticket() -> None:
    response = client.post(
        "/api/v1/tickets/email-intake",
        json={
            "from_name": "Email User",
            "from_email": "email.user@example.com",
            "email_subject": "Invoice document attached",
            "email_body": "Hello, I attached my invoice document and need it processed.",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["requester_name"] == "Email User"
    assert data["requester_email"] == "email.user@example.com"
    assert data["subject"] == "Invoice document attached"
    assert data["description"] == "Hello, I attached my invoice document and need it processed."
    assert data["source"] == "email"
    assert len(data["messages"]) == 1
    assert data["messages"][0]["sender_type"] == "requester"


def test_email_intake_rejects_invalid_email() -> None:
    response = client.post(
        "/api/v1/tickets/email-intake",
        json={
            "from_name": "Invalid Email User",
            "from_email": "not-an-email",
            "email_subject": "Need help",
            "email_body": "Please help me.",
        },
    )

    assert response.status_code == 422