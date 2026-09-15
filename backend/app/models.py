from typing import Optional
from pydantic import BaseModel, Field, field_validator


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = "ok"
    service: str = "hiver-ai-support-agent"


class AnalyzeRequest(BaseModel):
    """Inbound customer message analysis request."""
    message: str = Field(
        ...,
        min_length=1,
        description="Customer support message to analyze"
    )

    @field_validator("message")
    @classmethod
    def validate_message_not_empty(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Message cannot be empty or contain only whitespace.")
        return trimmed


class HistoricalMatch(BaseModel):
    """Historical customer resolution match details."""
    customer_message: str
    support_response: str


class AnalyzeResponse(BaseModel):
    """Support agent pipeline analysis response.

    At this stage, fields return placeholder values as specified in Step 2.
    """
    message: str
    intent: Optional[str] = None
    confidence: Optional[float] = None
    historical_match: Optional[HistoricalMatch] = None
    similarity: Optional[float] = None
    draft_reply: Optional[str] = None
    decision: Optional[str] = None
    decision_reason: Optional[str] = None
