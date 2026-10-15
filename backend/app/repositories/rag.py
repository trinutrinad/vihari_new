"""RAG knowledge store data access."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import KnowledgeChunk, KnowledgeDocument


class RagRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_document(self, document_id: uuid.UUID) -> KnowledgeDocument | None:
        return self.db.scalar(
            select(KnowledgeDocument)
            .where(KnowledgeDocument.id == document_id)
            .options(selectinload(KnowledgeDocument.chunks)),
        )

    def get_by_source_uri(self, source_uri: str) -> KnowledgeDocument | None:
        return self.db.scalar(
            select(KnowledgeDocument)
            .where(KnowledgeDocument.source_uri == source_uri)
            .options(selectinload(KnowledgeDocument.chunks)),
        )

    def list_documents(self, *, limit: int = 50) -> list[KnowledgeDocument]:
        return list(
            self.db.scalars(
                select(KnowledgeDocument)
                .options(selectinload(KnowledgeDocument.chunks))
                .order_by(KnowledgeDocument.created_at.desc())
                .limit(limit),
            ).all(),
        )

    def list_chunks(self, *, limit: int = 500) -> list[KnowledgeChunk]:
        return list(
            self.db.scalars(
                select(KnowledgeChunk)
                .options(selectinload(KnowledgeChunk.document))
                .order_by(KnowledgeChunk.created_at.desc())
                .limit(limit),
            ).all(),
        )

    def add_document(self, document: KnowledgeDocument) -> KnowledgeDocument:
        self.db.add(document)
        self.db.flush()
        return document

    def delete_chunks_for_document(self, document_id: uuid.UUID) -> None:
        chunks = list(
            self.db.scalars(
                select(KnowledgeChunk).where(KnowledgeChunk.document_id == document_id),
            ).all(),
        )
        for chunk in chunks:
            self.db.delete(chunk)
        self.db.flush()
