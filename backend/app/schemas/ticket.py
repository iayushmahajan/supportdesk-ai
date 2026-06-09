import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field

from app.models.ticket import (
    AgentRunStatus,
    AutomationEventStatus,
    MessageSenderType,
    TicketCategory,
    TicketPriority,
    TicketSource,
    TicketStatus,
)


class TicketCreate(BaseModel):
    requester_name: str = Field(min_length=1, max_length=120)
    requester_email: EmailStr
    subject: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    source: TicketSource = TicketSource.FORM


class EmailTicketCreate(BaseModel):
    from_name: str = Field(min_length=1, max_length=120)
    from_email: EmailStr
    email_subject: str = Field(min_length=1, max_length=255)
    email_body: str = Field(min_length=1)


class TicketStatusUpdate(BaseModel):
    status: TicketStatus


class TicketMessageRead(BaseModel):
    id: uuid.UUID
    sender_type: MessageSenderType
    sender_name: str | None
    sender_email: str | None
    body: str
    created_at: datetime


class AgentRunRead(BaseModel):
    id: uuid.UUID
    agent_name: str
    execution_order: int
    status: AgentRunStatus
    input_json: dict[str, Any] | None
    output_json: dict[str, Any] | None
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime


class GeneratedResponseRead(BaseModel):
    id: uuid.UUID
    response_text: str
    tone: str
    is_approved: bool
    created_at: datetime


class AutomationEventRead(BaseModel):
    id: uuid.UUID
    event_type: str
    status: AutomationEventStatus
    provider: str
    payload_json: dict[str, Any] | None
    response_json: dict[str, Any] | None
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None


class TicketAttachmentRead(BaseModel):
    id: uuid.UUID
    file_name: str
    content_type: str | None
    file_size_bytes: int | None
    storage_path: str | None
    created_at: datetime


class TicketRead(BaseModel):
    id: uuid.UUID

    requester_name: str
    requester_email: EmailStr

    subject: str
    description: str
    source: TicketSource

    status: TicketStatus
    priority: TicketPriority
    category: TicketCategory

    suggested_department: str | None
    internal_summary: str | None

    created_at: datetime
    updated_at: datetime


class TicketDetailRead(TicketRead):
    messages: list[TicketMessageRead] = []
    agent_runs: list[AgentRunRead] = []
    generated_responses: list[GeneratedResponseRead] = []
    automation_events: list[AutomationEventRead] = []
    attachments: list[TicketAttachmentRead] = []