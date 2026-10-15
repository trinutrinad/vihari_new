"""AI provider abstraction — mock now, vendor LLMs later."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.config import get_settings


@dataclass
class AICompletion:
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    provider: str


class AIProvider(ABC):
    @abstractmethod
    def complete(self, *, system: str, user: str) -> AICompletion:
        raise NotImplementedError


class MockAIProvider(AIProvider):
    """Deterministic mock used for Phase 9 — no external LLM calls."""

    def complete(self, *, system: str, user: str) -> AICompletion:
        lower = user.lower()
        system_lower = system.lower()
        if "sources:" in lower or "grounded" in system_lower:
            content = (
                "Using the cited curated sources, here is a concise grounded answer. "
                "Confirm official timings and fees locally — seed knowledge is illustrative."
            )
        elif "plan" in lower or "itinerary" in lower or "trip" in lower:
            content = (
                "Here is a practical draft itinerary based on seeded destination data. "
                "Official timings and fees are not verified — confirm before travel."
            )
        elif "budget" in lower:
            content = (
                "Keep a daily buffer for local transport and meals. "
                "Seed estimates are illustrative only."
            )
        elif "food" in lower or "hotel" in lower:
            content = (
                "I can suggest demo hotels and restaurants near your destinations. "
                "These are marked seed/demo — not live inventory."
            )
        else:
            content = (
                "I can help plan Indian trips from your preferences "
                "(days, budget, interests). Try the trip planner form for a full itinerary."
            )
        return AICompletion(
            content=content,
            model="mock-travel-v1",
            prompt_tokens=max(len(system.split()) + len(user.split()), 1),
            completion_tokens=max(len(content.split()), 1),
            provider="mock",
        )


def get_ai_provider() -> AIProvider:
    settings = get_settings()
    if settings.ai_provider.lower() == "mock":
        return MockAIProvider()
    # Future: OpenAI / Azure / etc.
    return MockAIProvider()
