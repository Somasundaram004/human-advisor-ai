from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


def now() -> datetime:
    return datetime.now(timezone.utc)


class MemoryInput(BaseModel):
    kind: Literal["incident", "feeling", "fact", "feedback"]
    summary: str = Field(min_length=1, max_length=4000)
    details: dict[str, Any] = Field(default_factory=dict)
    sensitivity: Literal["normal", "sensitive", "restricted"] = "normal"


class AdviceInput(BaseModel):
    question: str = Field(min_length=1, max_length=8000)
    context: dict[str, Any] = Field(default_factory=dict)


class ActionRequest(BaseModel):
    action: Literal["send_api_request", "write_code", "run_command"]
    payload: dict[str, Any] = Field(default_factory=dict)
    reason: str = Field(min_length=1, max_length=2000)


class ApprovalInput(BaseModel):
    approved: bool
    comment: str = Field(default="", max_length=2000)


class VoiceInput(BaseModel):
    text: str = Field(min_length=1, max_length=8000)
    speaker: str = Field(default="human", max_length=100)