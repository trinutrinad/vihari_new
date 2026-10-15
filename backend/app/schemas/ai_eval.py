"""AI evaluation schemas (Phase 24)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

EvalKind = Literal["rag_grounded", "rag_refusal", "planner_smoke", "chat_smoke"]


class EvalCaseOut(BaseModel):
    id: str
    name: str
    kind: EvalKind
    description: str
    tags: list[str] = Field(default_factory=list)


class EvalCheckOut(BaseModel):
    name: str
    passed: bool
    detail: str = ""


class EvalCaseResultOut(BaseModel):
    case_id: str
    name: str
    kind: EvalKind
    passed: bool
    latency_ms: int
    checks: list[EvalCheckOut]
    output_preview: str | None = None
    error: str | None = None


class EvalRunRequest(BaseModel):
    case_ids: list[str] | None = Field(
        default=None,
        description="Optional subset of case ids; omit to run the full suite.",
    )


class EvalRunOut(BaseModel):
    run_id: str
    started_at: datetime
    finished_at: datetime
    total: int
    passed: int
    failed: int
    pass_rate: float
    results: list[EvalCaseResultOut]
    metrics: dict[str, Any] = Field(default_factory=dict)
    notice: str = (
        "Deterministic mock evaluation suite for RAG grounding, refusal, "
        "planner smoke, and chat smoke. Not a substitute for human review "
        "or production LLM red-teaming."
    )
