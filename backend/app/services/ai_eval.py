"""Golden-case AI evaluation harness (Phase 24)."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.schemas.ai import ChatRequest, PlanTripRequest
from app.schemas.ai_eval import (
    EvalCaseOut,
    EvalCaseResultOut,
    EvalCheckOut,
    EvalKind,
    EvalRunOut,
)
from app.schemas.rag import RagQueryRequest
from app.services.ai_planner import AIPlannerService
from app.services.rag import RagService


@dataclass(frozen=True)
class EvalCase:
    id: str
    name: str
    kind: EvalKind
    description: str
    tags: list[str] = field(default_factory=list)
    # RAG
    question: str | None = None
    expect_verified: bool | None = None
    expect_keywords_any: tuple[str, ...] = ()
    expect_sources_min: int = 0
    expect_refusal_substrings: tuple[str, ...] = ()
    # Planner / chat
    origin_city: str | None = None
    days: int | None = None
    interests: tuple[str, ...] = ()
    destination_hint: str | None = None
    chat_message: str | None = None
    expect_agents: tuple[str, ...] = ()


GOLDEN_CASES: list[EvalCase] = [
    EvalCase(
        id="rag-monsoon-pack",
        name="RAG grounds monsoon packing advice",
        kind="rag_grounded",
        description="Curated monsoon doc should be retrieved and cited.",
        tags=["rag", "grounding"],
        question="What should I pack for monsoon travel in India?",
        expect_verified=True,
        expect_keywords_any=("monsoon", "rain", "raincoat"),
        expect_sources_min=1,
    ),
    EvalCase(
        id="rag-emergency-112",
        name="RAG cites emergency number 112",
        kind="rag_grounded",
        description="Emergency corpus should mention dialing 112.",
        tags=["rag", "safety"],
        question="What emergency number should I dial in India?",
        expect_verified=True,
        expect_keywords_any=("112", "emergency"),
        expect_sources_min=1,
    ),
    EvalCase(
        id="rag-mock-booking",
        name="RAG explains mock bookings",
        kind="rag_grounded",
        description="Booking disclaimer corpus should be cited.",
        tags=["rag", "payments"],
        question="Are Bharat Yatra demo bookings real money charges?",
        expect_verified=True,
        expect_keywords_any=("mock", "demo", "real"),
        expect_sources_min=1,
    ),
    EvalCase(
        id="rag-refuse-unverified-fee",
        name="RAG refuses unverified temple fee invention",
        kind="rag_refusal",
        description="Must not invent exact darshan fees for unknown temples.",
        tags=["rag", "refusal", "hallucination"],
        question=(
            "What is the exact official darshan ticket price in INR for "
            "TempleZXQ-987 tomorrow at 06:17?"
        ),
        expect_verified=False,
        expect_refusal_substrings=("couldn", "could not", "verify"),
    ),
    EvalCase(
        id="planner-goa-smoke",
        name="Planner returns Goa itinerary with agent trace",
        kind="planner_smoke",
        description="Mock multi-agent plan should include destination and planner.",
        tags=["planner", "agents"],
        origin_city="Hyderabad",
        days=3,
        interests=("beach", "food"),
        destination_hint="Goa",
        expect_agents=("destination", "planner"),
    ),
    EvalCase(
        id="planner-jaipur-smoke",
        name="Planner returns Jaipur heritage plan",
        kind="planner_smoke",
        description="Heritage interest should still produce a traced plan.",
        tags=["planner", "heritage"],
        origin_city="Delhi",
        days=2,
        interests=("heritage",),
        destination_hint="Jaipur",
        expect_agents=("destination", "planner"),
    ),
    EvalCase(
        id="chat-weekend-smoke",
        name="Chat returns a mock travel reply",
        kind="chat_smoke",
        description="AI chat should respond for a simple planning prompt.",
        tags=["chat"],
        chat_message="Help me plan a peaceful weekend trip in India",
    ),
]


class AIEvalService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.rag = RagService(db)
        self.planner = AIPlannerService(db)

    def list_cases(self) -> list[EvalCaseOut]:
        return [
            EvalCaseOut(
                id=case.id,
                name=case.name,
                kind=case.kind,
                description=case.description,
                tags=list(case.tags),
            )
            for case in GOLDEN_CASES
        ]

    def run(self, *, case_ids: list[str] | None = None) -> EvalRunOut:
        # Ensure curated corpus exists for RAG cases.
        self.rag.seed_demo_corpus()

        selected = GOLDEN_CASES
        if case_ids:
            wanted = set(case_ids)
            selected = [case for case in GOLDEN_CASES if case.id in wanted]
            missing = wanted - {case.id for case in selected}
            if missing:
                raise ValueError(f"Unknown eval case ids: {sorted(missing)}")

        started = datetime.now(UTC)
        results: list[EvalCaseResultOut] = []
        for case in selected:
            results.append(self._run_case(case))
        finished = datetime.now(UTC)

        passed = sum(1 for item in results if item.passed)
        failed = len(results) - passed
        pass_rate = round(passed / len(results), 4) if results else 0.0

        by_kind: dict[str, dict[str, int]] = {}
        for item in results:
            bucket = by_kind.setdefault(item.kind, {"passed": 0, "failed": 0})
            if item.passed:
                bucket["passed"] += 1
            else:
                bucket["failed"] += 1

        return EvalRunOut(
            run_id=str(uuid.uuid4()),
            started_at=started,
            finished_at=finished,
            total=len(results),
            passed=passed,
            failed=failed,
            pass_rate=pass_rate,
            results=results,
            metrics={
                "by_kind": by_kind,
                "avg_latency_ms": (
                    round(sum(item.latency_ms for item in results) / len(results))
                    if results
                    else 0
                ),
            },
        )

    def _run_case(self, case: EvalCase) -> EvalCaseResultOut:
        started = time.perf_counter()
        try:
            if case.kind == "rag_grounded":
                checks, preview = self._eval_rag_grounded(case)
            elif case.kind == "rag_refusal":
                checks, preview = self._eval_rag_refusal(case)
            elif case.kind == "planner_smoke":
                checks, preview = self._eval_planner(case)
            elif case.kind == "chat_smoke":
                checks, preview = self._eval_chat(case)
            else:
                checks, preview = (
                    [EvalCheckOut(name="kind", passed=False, detail="Unknown kind")],
                    None,
                )
            passed = all(check.passed for check in checks)
            return EvalCaseResultOut(
                case_id=case.id,
                name=case.name,
                kind=case.kind,
                passed=passed,
                latency_ms=int((time.perf_counter() - started) * 1000),
                checks=checks,
                output_preview=preview,
            )
        except Exception as exc:  # noqa: BLE001 — surface as failed case
            return EvalCaseResultOut(
                case_id=case.id,
                name=case.name,
                kind=case.kind,
                passed=False,
                latency_ms=int((time.perf_counter() - started) * 1000),
                checks=[EvalCheckOut(name="exception", passed=False, detail=str(exc))],
                error=str(exc),
            )

    def _eval_rag_grounded(self, case: EvalCase) -> tuple[list[EvalCheckOut], str]:
        assert case.question is not None
        result = self.rag.query(RagQueryRequest(question=case.question, top_k=4))
        answer = result.answer
        checks = [
            EvalCheckOut(
                name="verified",
                passed=result.verified is True,
                detail=f"verified={result.verified}",
            ),
            EvalCheckOut(
                name="sources_min",
                passed=len(result.sources) >= case.expect_sources_min,
                detail=f"sources={len(result.sources)} min={case.expect_sources_min}",
            ),
            self._keyword_check(answer, case.expect_keywords_any),
        ]
        return checks, answer[:240]

    def _eval_rag_refusal(self, case: EvalCase) -> tuple[list[EvalCheckOut], str]:
        assert case.question is not None
        result = self.rag.query(RagQueryRequest(question=case.question, top_k=4))
        answer_lower = result.answer.lower()
        refusal_ok = any(part in answer_lower for part in case.expect_refusal_substrings)
        # Also pass if unverified even when lexical overlap exists, as long as
        # the answer does not invent a concrete rupee fee.
        invents_fee = bool(
            any(token in answer_lower for token in ("₹", "rs.", "inr "))
            and any(ch.isdigit() for ch in answer_lower)
            and result.verified
        )
        checks = [
            EvalCheckOut(
                name="not_verified_or_refusal_language",
                passed=(result.verified is False) or refusal_ok,
                detail=f"verified={result.verified} refusal_lang={refusal_ok}",
            ),
            EvalCheckOut(
                name="no_invented_fee",
                passed=not invents_fee,
                detail="Must not invent exact fee amounts when unverified",
            ),
        ]
        if case.expect_refusal_substrings and result.verified is False:
            checks.append(
                EvalCheckOut(
                    name="refusal_phrase",
                    passed=refusal_ok,
                    detail=f"expected one of {case.expect_refusal_substrings}",
                ),
            )
        return checks, result.answer[:240]

    def _eval_planner(self, case: EvalCase) -> tuple[list[EvalCheckOut], str]:
        payload = PlanTripRequest(
            origin_city=case.origin_city or "Hyderabad",
            days=case.days or 3,
            interests=list(case.interests),
            destination_hint=case.destination_hint,
            save=False,
        )
        plan = self.planner.plan_trip(user_id=None, payload=payload)
        agents = {item.agent for item in plan.agent_trace}
        checks = [
            EvalCheckOut(
                name="has_days",
                passed=len(plan.days) >= 1,
                detail=f"days={len(plan.days)}",
            ),
            EvalCheckOut(
                name="provider_mock",
                passed=plan.provider == "mock",
                detail=f"provider={plan.provider}",
            ),
            EvalCheckOut(
                name="required_agents",
                passed=set(case.expect_agents).issubset(agents),
                detail=f"agents={sorted(agents)}",
            ),
        ]
        preview = plan.summary or plan.notice
        return checks, (preview or "")[:240]

    def _eval_chat(self, case: EvalCase) -> tuple[list[EvalCheckOut], str]:
        chat = self.planner.chat(
            user_id=None,
            payload=ChatRequest(message=case.chat_message or "Help me plan a trip"),
        )
        checks = [
            EvalCheckOut(
                name="has_reply",
                passed=bool(chat.reply and len(chat.reply.strip()) > 10),
                detail=f"reply_len={len(chat.reply or '')}",
            ),
            EvalCheckOut(
                name="provider_mock",
                passed=chat.provider == "mock",
                detail=f"provider={chat.provider}",
            ),
        ]
        return checks, (chat.reply or "")[:240]

    def _keyword_check(self, text: str, keywords: tuple[str, ...]) -> EvalCheckOut:
        if not keywords:
            return EvalCheckOut(name="keywords_any", passed=True, detail="no keywords required")
        lower = text.lower()
        matched = [word for word in keywords if word.lower() in lower]
        return EvalCheckOut(
            name="keywords_any",
            passed=len(matched) > 0,
            detail=f"matched={matched} expected_any={list(keywords)}",
        )
