import uuid
from typing import Any

from pydantic import BaseModel, Field

from app.models.ticket import AutomationEventStatus


class AutomationWebhookTestRequest(BaseModel):
    message: str = Field(default="SupportDesk AI webhook test")


class AutomationCallbackRequest(BaseModel):
    ticket_id: uuid.UUID
    event_type: str
    status: AutomationEventStatus = AutomationEventStatus.SENT
    provider: str = "n8n"
    response_json: dict[str, Any] | None = None
    error_message: str | None = None


class AutomationEventCreate(BaseModel):
    ticket_id: uuid.UUID
    event_type: str
    status: AutomationEventStatus = AutomationEventStatus.PENDING
    provider: str = "n8n"
    payload_json: dict[str, Any] | None = None
    response_json: dict[str, Any] | None = None
    error_message: str | None = None