from typing import Any

from pydantic import BaseModel, Field

from app.models.ticket import TicketCategory, TicketPriority


class TicketAIResult(BaseModel):
    """
    Validated structured output from the AI ticket processor.

    The LLM must return this shape. If the LLM fails, the fallback processor
    also returns this same shape.
    """

    category: TicketCategory
    priority: TicketPriority
    suggested_department: str = Field(min_length=1, max_length=120)

    extracted_entities: dict[str, Any] = Field(default_factory=dict)
    missing_information: list[str] = Field(default_factory=list)

    internal_summary: str = Field(min_length=1)
    response_draft: str = Field(min_length=1)


class TicketAIProcessingResponse(BaseModel):
    ticket_id: str
    ai_result: TicketAIResult