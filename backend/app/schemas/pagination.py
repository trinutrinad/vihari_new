"""Pagination helpers for list endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PageMeta(BaseModel):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total: int = Field(ge=0)
    total_pages: int = Field(ge=0)


class PaginatedData[T](BaseModel):
    items: list[T]
    meta: PageMeta
