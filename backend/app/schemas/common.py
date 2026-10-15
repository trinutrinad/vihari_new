"""Shared API response schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ApiResponse[T](BaseModel):
    success: bool = True
    message: str = "OK"
    data: T | None = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict | list | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


class HealthData(BaseModel):
    status: str = Field(description="Service health status")
    service: str
    environment: str
    timestamp: datetime
    version: str
    checks: dict[str, str] | None = None
