"""Reviews API routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.common import ApiResponse
from app.schemas.reviews import ReviewCreate, ReviewOut, ReviewUpdate
from app.services.reviews import ReviewService

router = APIRouter(prefix="/reviews")


@router.get("", response_model=ApiResponse[list[ReviewOut]])
def list_reviews(
    db: DbSession,
    target_type: Annotated[str, Query()],
    target_id: Annotated[UUID, Query()],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> ApiResponse[list[ReviewOut]]:
    data = ReviewService(db).list_reviews(
        target_type=target_type,
        target_id=target_id,
        limit=limit,
    )
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/me", response_model=ApiResponse[list[ReviewOut]])
def list_my_reviews(
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[list[ReviewOut]]:
    data = ReviewService(db).list_mine(user_id=current_user.id)
    return ApiResponse(success=True, message="OK", data=data)


@router.post(
    "",
    response_model=ApiResponse[ReviewOut],
    status_code=status.HTTP_201_CREATED,
)
def upsert_review(
    payload: ReviewCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[ReviewOut]:
    data = ReviewService(db).upsert_review(user_id=current_user.id, payload=payload)
    return ApiResponse(success=True, message="Review saved", data=data)


@router.get("/{review_id}", response_model=ApiResponse[ReviewOut])
def get_review(review_id: UUID, db: DbSession) -> ApiResponse[ReviewOut]:
    data = ReviewService(db).get_review(review_id=review_id)
    return ApiResponse(success=True, message="OK", data=data)


@router.patch("/{review_id}", response_model=ApiResponse[ReviewOut])
def update_review(
    review_id: UUID,
    payload: ReviewUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[ReviewOut]:
    data = ReviewService(db).update_review(
        review_id=review_id,
        user_id=current_user.id,
        payload=payload,
    )
    return ApiResponse(success=True, message="Review updated", data=data)


@router.delete("/{review_id}", response_model=ApiResponse[dict])
def delete_review(
    review_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[dict]:
    ReviewService(db).delete_review(review_id=review_id, user_id=current_user.id)
    return ApiResponse(success=True, message="Review hidden", data={"deleted": True})
