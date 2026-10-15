"""RAG ingest, retrieve, rerank, and grounded answer generation."""

from __future__ import annotations

import hashlib
import json
import math
import re
import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.agents.provider import AIProvider, get_ai_provider
from app.core.exceptions import NotFoundError
from app.models import KnowledgeChunk, KnowledgeDocument
from app.models.enums import KnowledgeSourceType
from app.repositories.rag import RagRepository
from app.schemas.rag import (
    RagChunkOut,
    RagDocumentOut,
    RagIngestOut,
    RagIngestRequest,
    RagQueryOut,
    RagQueryRequest,
    RagSourceOut,
)
from app.services.embedding_provider import (
    EmbeddingProvider,
    cosine_similarity,
    get_embedding_provider,
)
from app.services.rag_chunking import chunk_text, estimate_token_count

TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
MIN_SCORE = 0.18
EXACT_FEE_RE = re.compile(
    r"\b(exact|official)\b.*\b(fee|price|ticket|cost)\b|"
    r"\b(fee|price|ticket)\b.*\b(exact|official)\b|"
    r"darshan ticket price",
    re.IGNORECASE,
)


@dataclass
class ScoredChunk:
    chunk: KnowledgeChunk
    score: float


class RagService:
    def __init__(
        self,
        db: Session,
        *,
        embeddings: EmbeddingProvider | None = None,
        ai: AIProvider | None = None,
    ) -> None:
        self.db = db
        self.repo = RagRepository(db)
        self.embeddings = embeddings or get_embedding_provider()
        self.ai = ai or get_ai_provider()

    def list_documents(self, *, limit: int = 50) -> list[RagDocumentOut]:
        return [self._document_out(doc) for doc in self.repo.list_documents(limit=limit)]

    def get_document(self, document_id: uuid.UUID) -> RagDocumentOut:
        document = self.repo.get_document(document_id)
        if document is None:
            raise NotFoundError("Knowledge document not found")
        return self._document_out(document)

    def ingest(self, payload: RagIngestRequest) -> RagIngestOut:
        source_uri = payload.source_uri or (
            f"curated://{hashlib.sha1(payload.title.encode()).hexdigest()[:12]}"
        )
        existing = self.repo.get_by_source_uri(source_uri)
        checksum = hashlib.sha256(payload.text.encode("utf-8")).hexdigest()

        if existing is not None:
            document = existing
            document.title = payload.title.strip()
            document.source_type = payload.source_type.value
            document.language = payload.language
            document.checksum = checksum
            document.raw_text = payload.text
            self.repo.delete_chunks_for_document(document.id)
        else:
            document = KnowledgeDocument(
                title=payload.title.strip(),
                source_type=payload.source_type.value,
                source_uri=source_uri,
                language=payload.language,
                checksum=checksum,
                raw_text=payload.text,
            )
            self.repo.add_document(document)

        pieces = chunk_text(payload.text)
        vectors = self.embeddings.embed_many(pieces)
        for index, (content, vector) in enumerate(zip(pieces, vectors, strict=True)):
            self.db.add(
                KnowledgeChunk(
                    document_id=document.id,
                    chunk_index=index,
                    content=content,
                    token_count=estimate_token_count(content),
                    embedding_model=self.embeddings.model_name,
                    embedding_ref=json.dumps(vector),
                ),
            )
        self.db.commit()
        refreshed = self.repo.get_document(document.id)
        assert refreshed is not None
        return RagIngestOut(
            document=self._document_out(refreshed),
            chunks_created=len(pieces),
            embedding_model=self.embeddings.model_name,
        )

    def seed_demo_corpus(self) -> list[RagDocumentOut]:
        created: list[RagDocumentOut] = []
        for title, source_uri, source_type, text in DEMO_KNOWLEDGE:
            existing = self.repo.get_by_source_uri(source_uri)
            if existing is not None:
                created.append(self._document_out(existing))
                continue
            result = self.ingest(
                RagIngestRequest(
                    title=title,
                    text=text,
                    source_type=source_type,
                    source_uri=source_uri,
                    language="en",
                ),
            )
            created.append(result.document)
        return created

    def query(self, payload: RagQueryRequest) -> RagQueryOut:
        scored = self._retrieve(payload.question, top_k=payload.top_k)
        if not scored or scored[0].score < MIN_SCORE:
            return RagQueryOut(
                answer=(
                    "I couldn't verify this information from the curated knowledge base. "
                    "Try asking about monsoon travel, temple etiquette basics, or seed/demo "
                    "booking disclaimers."
                ),
                verified=False,
                sources=[],
                chunks=[],
                model="mock-travel-v1",
                embedding_model=self.embeddings.model_name,
            )

        if self._requires_unverified_refusal(payload.question, scored):
            return RagQueryOut(
                answer=(
                    "I couldn't verify this information from the curated knowledge base. "
                    "Exact official fees, tickets, and timings are not confirmed here — "
                    "check temple or tourism sources directly."
                ),
                verified=False,
                sources=[],
                chunks=[],
                model="mock-travel-v1",
                embedding_model=self.embeddings.model_name,
            )

        sources = [
            RagSourceOut(
                document_id=item.chunk.document_id,
                title=item.chunk.document.title if item.chunk.document else "Untitled",
                source_type=(
                    item.chunk.document.source_type if item.chunk.document else "curated"
                ),
                source_uri=item.chunk.document.source_uri if item.chunk.document else None,
                chunk_index=item.chunk.chunk_index,
                excerpt=item.chunk.content[:280],
                score=round(item.score, 4),
            )
            for item in scored
        ]
        chunk_outs = [
            RagChunkOut(
                id=item.chunk.id,
                document_id=item.chunk.document_id,
                chunk_index=item.chunk.chunk_index,
                content=item.chunk.content,
                score=round(item.score, 4),
                document_title=(
                    item.chunk.document.title if item.chunk.document else "Untitled"
                ),
                source_type=(
                    item.chunk.document.source_type if item.chunk.document else "curated"
                ),
                source_uri=item.chunk.document.source_uri if item.chunk.document else None,
            )
            for item in scored
        ]

        context = "\n\n".join(
            f"[{idx + 1}] ({src.title} / {src.source_type})\n{src.excerpt}"
            for idx, src in enumerate(sources)
        )
        system = (
            "You are Bharat Yatra's grounded travel assistant. "
            "Answer ONLY using the provided sources. "
            "If sources are insufficient, say you could not verify the information. "
            "Cite source numbers like [1]."
        )
        user = f"Question: {payload.question}\n\nSources:\n{context}"
        completion = self.ai.complete(system=system, user=user)
        answer = self._grounded_answer(payload.question, sources, completion.content)

        return RagQueryOut(
            answer=answer,
            verified=True,
            sources=sources,
            chunks=chunk_outs,
            model=completion.model,
            embedding_model=self.embeddings.model_name,
        )

    def _requires_unverified_refusal(
        self,
        question: str,
        scored: list[ScoredChunk],
    ) -> bool:
        """Refuse inventing exact fees/timings when corpus only has general guidance."""
        if not EXACT_FEE_RE.search(question):
            return False
        joined = " ".join(item.chunk.content.lower() for item in scored)
        # Corpus must explicitly contain a numeric fee claim to answer exactly.
        has_numeric_fee = bool(
            re.search(r"(₹|rs\.?|inr)\s*\d+", joined)
            or re.search(r"\d+\s*(₹|rs\.?|inr|rupees)", joined)
        )
        return not has_numeric_fee

    def _retrieve(self, question: str, *, top_k: int) -> list[ScoredChunk]:
        query_vector = self.embeddings.embed(question)
        query_tokens = set(TOKEN_RE.findall(question.lower()))
        scored: list[ScoredChunk] = []
        for chunk in self.repo.list_chunks(limit=500):
            vector = self._parse_embedding(chunk.embedding_ref)
            if vector is None:
                vector = self.embeddings.embed(chunk.content)
            semantic = cosine_similarity(query_vector, vector)
            lexical = self._lexical_score(query_tokens, chunk.content)
            score = (0.7 * semantic) + (0.3 * lexical)
            if score > 0:
                scored.append(ScoredChunk(chunk=chunk, score=score))
        scored.sort(key=lambda item: item.score, reverse=True)
        # Light rerank: boost exact phrase matches
        q_lower = question.lower()
        for item in scored[: max(top_k * 3, top_k)]:
            if q_lower[:40] and q_lower[:40] in item.chunk.content.lower():
                item.score += 0.05
        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]

    def _lexical_score(self, query_tokens: set[str], content: str) -> float:
        if not query_tokens:
            return 0.0
        content_tokens = set(TOKEN_RE.findall(content.lower()))
        if not content_tokens:
            return 0.0
        overlap = len(query_tokens & content_tokens)
        return overlap / math.sqrt(len(query_tokens) * len(content_tokens))

    def _parse_embedding(self, embedding_ref: str | None) -> list[float] | None:
        if not embedding_ref:
            return None
        try:
            data = json.loads(embedding_ref)
        except json.JSONDecodeError:
            return None
        if not isinstance(data, list):
            return None
        return [float(value) for value in data]

    def _grounded_answer(
        self,
        question: str,
        sources: list[RagSourceOut],
        llm_content: str,
    ) -> str:
        lead = sources[0].excerpt.strip()
        cites = ", ".join(f"[{idx + 1}]" for idx in range(len(sources)))
        if "could not verify" in llm_content.lower() or "couldn't verify" in llm_content.lower():
            return (
                "I couldn't verify this information from the curated knowledge base "
                f"with enough confidence. Closest excerpts: {cites}."
            )
        return (
            f"{lead} "
            f"(Sources {cites}. Question: {question.strip()}. "
            "Confirm details locally before travel.)"
        )

    def _document_out(self, document: KnowledgeDocument) -> RagDocumentOut:
        return RagDocumentOut(
            id=document.id,
            title=document.title,
            source_type=document.source_type,
            source_uri=document.source_uri,
            language=document.language,
            chunk_count=len(document.chunks or []),
            created_at=document.created_at,
        )


DEMO_KNOWLEDGE: list[tuple[str, str, KnowledgeSourceType, str]] = [
    (
        "[SEED/DEMO] Monsoon travel basics for India",
        "seed://monsoon-travel-basics",
        KnowledgeSourceType.CURATED,
        (
            "Monsoon months vary by region across India. In much of peninsular India, "
            "June to September brings heavy rain, slippery roads, and occasional "
            "transport delays. Carry a light raincoat, waterproof bag covers, and allow "
            "buffer time between long-distance connections. Hill stations may see "
            "landslides — check local advisories before mountain travel. "
            "This is curated demo guidance, not an official weather bulletin."
        ),
    ),
    (
        "[SEED/DEMO] Temple visit etiquette (general)",
        "seed://temple-etiquette-general",
        KnowledgeSourceType.CURATED,
        (
            "General temple etiquette often includes modest clothing that covers "
            "shoulders and knees, removing footwear where required, and keeping voices "
            "low inside sanctums. Photography rules differ by temple — always follow "
            "on-site signs and staff instructions. Darshan timings, special entry "
            "tickets, and dress codes are NOT verified in this dataset. "
            "Confirm with official temple or tourism sources before visiting."
        ),
    ),
    (
        "[SEED/DEMO] Mock booking and payment disclaimer",
        "seed://mock-booking-disclaimer",
        KnowledgeSourceType.CURATED,
        (
            "Bharat Yatra demo bookings and payments are mock flows for product "
            "development. No real hotel inventory is reserved and no real money is "
            "charged. Coupons like BYDEMO10 are seed/demo only. For real travel, use "
            "verified booking providers and confirm cancellation policies directly."
        ),
    ),
    (
        "[SEED/DEMO] Family-friendly trip planning tips",
        "seed://family-trip-tips",
        KnowledgeSourceType.CURATED,
        (
            "For family trips in India, plan shorter daily transfers, midday rest for "
            "heat, and destinations with reliable restrooms and drinking water access. "
            "Keep digital and paper copies of IDs. Prefer well-lit evening areas and "
            "share live location with a trusted contact. Seed destination lists are "
            "illustrative — verify facilities on arrival."
        ),
    ),
    (
        "[SEED/DEMO] Emergency numbers reminder",
        "seed://emergency-numbers-reminder",
        KnowledgeSourceType.CURATED,
        (
            "In India, dial 112 for the national emergency response number. "
            "Tourist police and local hospital contacts vary by city. "
            "Bharat Yatra mock SOS creates a support ticket only — it does not "
            "dispatch emergency services. Always use official emergency channels "
            "in a real crisis."
        ),
    ),
]
