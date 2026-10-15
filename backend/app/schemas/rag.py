"""RAG API schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import KnowledgeSourceType


class RagIngestRequest(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    text: str = Field(min_length=20, max_length=50_000)
    source_type: KnowledgeSourceType = KnowledgeSourceType.CURATED
    source_uri: str | None = Field(default=None, max_length=500)
    language: str = Field(default="en", max_length=16)


class RagQueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    top_k: int = Field(default=4, ge=1, le=10)


class RagChunkOut(BaseModel):
    id: UUID
    document_id: UUID
    chunk_index: int
    content: str
    score: float
    document_title: str
    source_type: str
    source_uri: str | None = None


class RagSourceOut(BaseModel):
    document_id: UUID
    title: str
    source_type: str
    source_uri: str | None = None
    chunk_index: int
    excerpt: str
    score: float


class RagQueryOut(BaseModel):
    answer: str
    verified: bool
    sources: list[RagSourceOut]
    chunks: list[RagChunkOut]
    model: str
    embedding_model: str
    notice: str = (
        "Answers cite curated/seed knowledge only. "
        "Official temple timings and fees are not verified here."
    )


class RagDocumentOut(BaseModel):
    id: UUID
    title: str
    source_type: str
    source_uri: str | None = None
    language: str
    chunk_count: int
    created_at: datetime | None = None


class RagIngestOut(BaseModel):
    document: RagDocumentOut
    chunks_created: int
    embedding_model: str
