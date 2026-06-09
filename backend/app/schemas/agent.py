from typing import Any

from pydantic import BaseModel, Field

from app.models.ticket import TicketCategory, TicketPriority


class IntakeAgentOutput(BaseModel):
    intent: str = Field(min_length=1)
    extracted_entities: dict[str, Any] = Field(default_factory=dict)


class ClassificationAgentOutput(BaseModel):
    category: TicketCategory
    reasoning: str = Field(min_length=1)


class PriorityAgentOutput(BaseModel):
    priority: TicketPriority
    reasoning: str = Field(min_length=1)


class RoutingAgentOutput(BaseModel):
    suggested_department: str = Field(min_length=1, max_length=120)
    reasoning: str = Field(min_length=1)


class MissingInfoAgentOutput(BaseModel):
    missing_information: list[str] = Field(default_factory=list)


class SummaryAgentOutput(BaseModel):
    internal_summary: str = Field(min_length=1)


class ResponseDraftAgentOutput(BaseModel):
    response_draft: str = Field(min_length=1)


class MultiAgentWorkflowResult(BaseModel):
    category: TicketCategory
    priority: TicketPriority
    suggested_department: str
    extracted_entities: dict[str, Any]
    missing_information: list[str]
    internal_summary: str
    response_draft: str