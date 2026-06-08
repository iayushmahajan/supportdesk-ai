from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def valid_ticket_payload() -> dict[str, str]:
    return {
        "requester_name": "Test User",
        "requester_email": "test.user@example.com",
        "subject": "Dashboard is not loading",
        "description": "The dashboard keeps spinning and never loads.",
        "source": "form",
    }


def test_create_ticket_returns_created_ticket() -> None:
    response = client.post("/api/v1/tickets", json=valid_ticket_payload())

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["requester_name"] == "Test User"
    assert data["requester_email"] == "test.user@example.com"
    assert data["subject"] == "Dashboard is not loading"
    assert data["status"] == "open"
    assert data["priority"] == "unassigned"
    assert data["category"] == "unclassified"


def test_create_ticket_rejects_invalid_email() -> None:
    payload = valid_ticket_payload()
    payload["requester_email"] = "not-an-email"

    response = client.post("/api/v1/tickets", json=payload)

    assert response.status_code == 422


def test_list_tickets_returns_created_tickets() -> None:
    client.post("/api/v1/tickets", json=valid_ticket_payload())

    response = client.get("/api/v1/tickets")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["subject"] == "Dashboard is not loading"


def test_get_ticket_detail_returns_messages() -> None:
    create_response = client.post("/api/v1/tickets", json=valid_ticket_payload())
    ticket_id = create_response.json()["id"]

    detail_response = client.get(f"/api/v1/tickets/{ticket_id}")

    assert detail_response.status_code == 200

    data = detail_response.json()

    assert data["id"] == ticket_id
    assert data["subject"] == "Dashboard is not loading"
    assert len(data["messages"]) == 1
    assert data["messages"][0]["sender_type"] == "requester"
    assert data["messages"][0]["body"] == "The dashboard keeps spinning and never loads."


def test_get_ticket_detail_returns_404_for_unknown_ticket() -> None:
    response = client.get("/api/v1/tickets/11111111-1111-1111-1111-111111111111")

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_update_ticket_status() -> None:
    create_response = client.post("/api/v1/tickets", json=valid_ticket_payload())
    ticket_id = create_response.json()["id"]

    update_response = client.patch(
        f"/api/v1/tickets/{ticket_id}/status",
        json={"status": "in_progress"},
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["id"] == ticket_id
    assert data["status"] == "in_progress"


def test_update_ticket_status_rejects_invalid_status() -> None:
    create_response = client.post("/api/v1/tickets", json=valid_ticket_payload())
    ticket_id = create_response.json()["id"]

    update_response = client.patch(
        f"/api/v1/tickets/{ticket_id}/status",
        json={"status": "almost_done"},
    )

    assert update_response.status_code == 422