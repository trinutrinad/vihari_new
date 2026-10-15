# AI Architecture — Bharat Yatra

## Principles

1. No single giant AI function — specialized agents + orchestrator.
2. Agents never hit the database directly — only via controlled tools/services.
3. Factual answers require provenance; otherwise: "I couldn't verify this information."
4. Cost control: caching, token limits, history limits, usage tracking.

## Phase 10 status

Multi-agent pipeline is live (mock provider):

```
User request
  → TravelOrchestrator
    → DestinationAgent
    → HotelAgent / FoodAgent / GuideAgent
    → TransportAgent / WeatherAgent / SafetyAgent
    → BudgetAgent / BookingAgent (scaffold)
    → TravelPlannerAgent (final assemble)
```

- Shared `AgentContext` workspace + `agent_trace` / `tool_trace`
- Tools: places, hotels, restaurants, guides, transport, distance, weather (mock),
  safety hints (unverified), trip cost
- API: `GET /ai/agents`, `POST /ai/plan-trip`, `POST /ai/chat`

## Agents

| Agent | Status |
|-------|--------|
| DestinationAgent | live |
| HotelAgent | live |
| FoodAgent | live |
| GuideAgent | live |
| TransportAgent | live |
| WeatherAgent | live (mock) |
| SafetyAgent | live (unverified tips) |
| BudgetAgent | live |
| BookingAgent | scaffold |
| TravelPlannerAgent | live |

## Tools

`search_places`, `search_hotels`, `search_restaurants`, `search_guides`,
`search_transport`, `calculate_distance`, `calculate_trip_cost`, `get_weather`,
`find_nearby_safety`, `search_knowledge`, `resolve_city`, featured place fallback.

## RAG (Phase 23)

Pipeline (mock embeddings; pgvector later):

```
Ingest curated docs
  → chunk_text
  → MockEmbeddingProvider (hash bag-of-tokens)
  → store embedding_ref on knowledge_chunks
  → retrieve (cosine + lexical) → light rerank
  → grounded answer with source citations
```

- APIs: `POST /rag/query`, `GET /rag/documents`, `POST /rag/ingest` (admin), `POST /rag/seed-demo`
- UI: `/ask`
- Agent tool: `search_knowledge`
- Principle preserved: if retrieval score is weak → "I couldn't verify this information."
- Exact official fee/ticket questions refuse unless corpus has numeric fee claims.

## AI evaluation (Phase 24)

Golden-case suite (deterministic mock):

| Kind | What it checks |
|------|----------------|
| `rag_grounded` | verified + sources + keyword coverage |
| `rag_refusal` | no invented exact fees; refusal language |
| `planner_smoke` | days + mock provider + required agents |
| `chat_smoke` | non-empty mock reply |

- APIs: `GET /ai/eval/cases`, `POST /ai/eval/run` (ADMIN)
- UI: `/eval`
- Report includes pass rate, per-case checks, latency, metrics by kind
