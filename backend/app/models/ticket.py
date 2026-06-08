import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, Enum):
    UNASSIGNED = "unassigned"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketCategory(str, Enum):
    UNCLASSIFIED = "unclassified"
    TECHNICAL = "technical"
    BILLING = "billing"
    ACCOUNT = "account"
    DOCUMENT = "document"
    GENERAL = "general"


class TicketSource(str, Enum):
    FORM = "form"
    EMAIL = "email"


class MessageSenderType(str, Enum):
    REQUESTER = "requester"
    AGENT = "agent"
    SYSTEM = "system"


class AgentRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AutomationEventStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class Ticket(SQLModel, table=True):
    __tablename__ = "tickets"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    requester_name: str = Field(index=True, max_length=120)
    requester_email: str = Field(index=True, max_length=255)

    subject: str = Field(index=True, max_length=255)
    description: str

    source: TicketSource = Field(default=TicketSource.FORM)

    status: TicketStatus = Field(default=TicketStatus.OPEN, index=True)
    priority: TicketPriority = Field(default=TicketPriority.UNASSIGNED, index=True)
    category: TicketCategory = Field(default=TicketCategory.UNCLASSIFIED, index=True)

    suggested_department: str | None = Field(default=None, max_length=120)
    internal_summary: str | None = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    messages: list["TicketMessage"] = Relationship(
        back_populates="ticket",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    agent_runs: list["AgentRun"] = Relationship(
        back_populates="ticket",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    generated_responses: list["GeneratedResponse"] = Relationship(
        back_populates="ticket",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    automation_events: list["AutomationEvent"] = Relationship(
        back_populates="ticket",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    attachments: list["TicketAttachment"] = Relationship(
        back_populates="ticket",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class TicketMessage(SQLModel, table=True):
    __tablename__ = "ticket_messages"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    ticket_id: uuid.UUID = Field(foreign_key="tickets.id", index=True)

    sender_type: MessageSenderType = Field(default=MessageSenderType.REQUESTER)
    sender_name: str | None = Field(default=None, max_length=120)
    sender_email: str | None = Field(default=None, max_length=255)

    body: str

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    ticket: Ticket = Relationship(back_populates="messages")


class AgentRun(SQLModel, table=True):
    __tablename__ = "agent_runs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    ticket_id: uuid.UUID = Field(foreign_key="tickets.id", index=True)

    agent_name: str = Field(index=True, max_length=120)
    execution_order: int = Field(index=True)

    status: AgentRunStatus = Field(default=AgentRunStatus.PENDING, index=True)

    input_json: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSONB),
    )
    output_json: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSONB),
    )
    error_message: str | None = Field(default=None)

    started_at: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    ticket: Ticket = Relationship(back_populates="agent_runs")


class GeneratedResponse(SQLModel, table=True):
    __tablename__ = "generated_responses"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    ticket_id: uuid.UUID = Field(foreign_key="tickets.id", index=True)

    response_text: str
    tone: str = Field(default="professional", max_length=80)
    is_approved: bool = Field(default=False)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    ticket: Ticket = Relationship(back_populates="generated_responses")


class AutomationEvent(SQLModel, table=True):
    __tablename__ = "automation_events"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    ticket_id: uuid.UUID = Field(foreign_key="tickets.id", index=True)

    event_type: str = Field(index=True, max_length=120)
    status: AutomationEventStatus = Field(
        default=AutomationEventStatus.PENDING,
        index=True,
    )

    provider: str = Field(default="n8n", max_length=80)
    payload_json: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSONB),
    )
    response_json: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSONB),
    )
    error_message: str | None = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = Field(default=None)

    ticket: Ticket = Relationship(back_populates="automation_events")


class TicketAttachment(SQLModel, table=True):
    __tablename__ = "ticket_attachments"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    ticket_id: uuid.UUID = Field(foreign_key="tickets.id", index=True)

    file_name: str = Field(max_length=255)
    content_type: str | None = Field(default=None, max_length=120)
    file_size_bytes: int | None = Field(default=None)

    storage_path: str | None = Field(default=None, max_length=500)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    ticket: Ticket = Relationship(back_populates="attachments")