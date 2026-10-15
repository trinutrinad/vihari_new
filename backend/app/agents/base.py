"""Shared agent primitives — tools never expose raw DB sessions to LLM code."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:
    name: str
    ok: bool
    data: Any = None
    message: str = ""
    provenance: str = "seed_demo"


@dataclass
class AgentResult:
    agent: str
    ok: bool
    summary: str
    data: dict[str, Any] = field(default_factory=dict)
    tools_used: list[str] = field(default_factory=list)


@dataclass
class AgentContext:
    """Shared inputs + workspace for a multi-agent planning run."""

    origin_city: str
    days: int
    budget_inr: int | None = None
    interests: list[str] = field(default_factory=list)
    travelers: int = 2
    destination_hint: str | None = None
    free_text: str | None = None
    tool_trace: list[ToolResult] = field(default_factory=list)
    agent_trace: list[AgentResult] = field(default_factory=list)
    workspace: dict[str, Any] = field(default_factory=dict)

    def add_tool(self, result: ToolResult) -> None:
        self.tool_trace.append(result)

    def add_agent(self, result: AgentResult) -> None:
        self.agent_trace.append(result)


class BaseAgent(ABC):
    name: str = "base"

    @abstractmethod
    def run(self, ctx: AgentContext) -> AgentResult:
        raise NotImplementedError
