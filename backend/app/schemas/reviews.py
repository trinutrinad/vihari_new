"""Review API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

ReviewTargetLiteral = Literal[
    "place",
    "hotel",
    "restaurant",
    "guide",
    "activity",
]


class ReviewCreate(BaseModel):
    target_type: ReviewTargetLiteral
    target_id: UUID
    rating: int = Field(ge=1, le=5)
    title: str | None = Field(default=None, max_length=160)
    body: str | None = Field(default=None, max_length=2000)


class ReviewUpdate(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    title: str | None = Field(default=None, max_length=160)
    body: str | None = Field(default=None, max_length=2000)


class ReviewOut(BaseModel):
    id: UUID
    target_type: str
    target_id: UUID
    user_id: UUID
    rating: int
    title: str | None = None
    body: str | None = None
    author_name: str
    is_visible: bool = True
    is_moderated: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
    data_notice: str = (
        "Community reviews are user-submitted. Seed/demo content is fictional."
    )
