"""RAG API routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import DbSession, require_roles
from app.core.audit import audit_event
from app.models import User
from app.models.enums import UserRole
from app.schemas.common import ApiResponse
from app.schemas.rag import (
    RagDocumentOut,
    RagIngestOut,
    RagIngestRequest,
    RagQueryOut,
    RagQueryRequest,
)
from app.services.rag import RagService

router = APIRouter(prefix="/rag")

AdminUser = Annotated[
    User,
    Depends(
        require_roles(
            UserRole.ADMIN.value,
            UserRole.SUPER_ADMIN.value,
        ),
    ),
]


@router.post("/query", response_model=ApiResponse[RagQueryOut])
def rag_query(
    payload: RagQueryRequest,
    db: DbSession,
) -> ApiResponse[RagQueryOut]:
    data = RagService(db).query(payload)
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/documents", response_model=ApiResponse[list[RagDocumentOut]])
def list_rag_documents(
    db: DbSession,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> ApiResponse[list[RagDocumentOut]]:
    data = RagService(db).list_documents(limit=limit)
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/documents/{document_id}", response_model=ApiResponse[RagDocumentOut])
def get_rag_document(
    document_id: UUID,
    db: DbSession,
) -> ApiResponse[RagDocumentOut]:
    data = RagService(db).get_document(document_id)
    return ApiResponse(success=True, message="OK", data=data)


@router.post(
    "/ingest",
    response_model=ApiResponse[RagIngestOut],
    status_code=status.HTTP_201_CREATED,
)
def ingest_rag_document(
    payload: RagIngestRequest,
    db: DbSession,
    current_user: AdminUser,
) -> ApiResponse[RagIngestOut]:
    _ = current_user
    data = RagService(db).ingest(payload)
    audit_event(
        "rag.ingest",
        actor=str(current_user.id),
        title=payload.title,
        source_type=payload.source_type.value,
    )
    return ApiResponse(success=True, message="Document ingested", data=data)


@router.post(
    "/seed-demo",
    response_model=ApiResponse[list[RagDocumentOut]],
    status_code=status.HTTP_201_CREATED,
)
def seed_rag_demo(
    db: DbSession,
) -> ApiResponse[list[RagDocumentOut]]:
    """Idempotent demo corpus for local development and tests."""
    data = RagService(db).seed_demo_corpus()
    return ApiResponse(success=True, message="Demo knowledge seeded", data=data)
