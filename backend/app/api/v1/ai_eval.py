"""AI evaluation API routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import DbSession, require_roles
from app.core.audit import audit_event
from app.core.exceptions import ValidationAppError
from app.models import User
from app.models.enums import UserRole
from app.schemas.ai_eval import EvalCaseOut, EvalRunOut, EvalRunRequest
from app.schemas.common import ApiResponse
from app.services.ai_eval import AIEvalService

router = APIRouter(prefix="/ai/eval")

AdminUser = Annotated[
    User,
    Depends(
        require_roles(
            UserRole.ADMIN.value,
            UserRole.SUPER_ADMIN.value,
        ),
    ),
]


@router.get("/cases", response_model=ApiResponse[list[EvalCaseOut]])
def list_eval_cases(db: DbSession) -> ApiResponse[list[EvalCaseOut]]:
    data = AIEvalService(db).list_cases()
    return ApiResponse(success=True, message="OK", data=data)


@router.post("/run", response_model=ApiResponse[EvalRunOut])
def run_eval_suite(
    payload: EvalRunRequest,
    db: DbSession,
    current_user: AdminUser,
) -> ApiResponse[EvalRunOut]:
    _ = current_user
    try:
        data = AIEvalService(db).run(case_ids=payload.case_ids)
    except ValueError as exc:
        raise ValidationAppError(str(exc)) from exc
    audit_event(
        "ai.eval.run",
        actor=str(current_user.id),
        total=data.total,
        passed=data.passed,
        failed=data.failed,
    )
    return ApiResponse(success=True, message="Evaluation complete", data=data)
