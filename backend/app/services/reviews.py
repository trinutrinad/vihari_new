"""Reviews business logic."""

from __future__ import annotations

import json
import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationAppError
from app.models import UserReview
from app.models.enums import ReviewTargetType
from app.repositories.reviews import ReviewRepository
from app.schemas.reviews import ReviewCreate, ReviewOut, ReviewUpdate


class ReviewService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ReviewRepository(db)

    def list_reviews(
        self,
        *,
        target_type: str,
        target_id: uuid.UUID,
        limit: int = 50,
    ) -> list[ReviewOut]:
        self._ensure_target_exists(target_type, target_id)
        rows = self.repo.list_for_target(
            target_type=target_type,
            target_id=target_id,
            limit=limit,
        )
        return [self._to_out(row) for row in rows]

    def list_mine(self, *, user_id: uuid.UUID) -> list[ReviewOut]:
        return [self._to_out(row) for row in self.repo.list_for_user(user_id=user_id)]

    def get_review(self, *, review_id: uuid.UUID) -> ReviewOut:
        review = self.repo.get_by_id(review_id)
        if review is None or not review.is_visible:
            raise NotFoundError("Review not found")
        return self._to_out(review)

    def upsert_review(self, *, user_id: uuid.UUID, payload: ReviewCreate) -> ReviewOut:
        target_type = payload.target_type
        self._ensure_target_exists(target_type, payload.target_id)

        review = self.repo.get_user_review(
            user_id=user_id,
            target_type=target_type,
            target_id=payload.target_id,
        )
        meta = _meta_with_title({}, payload.title)
        if review is None:
            review = UserReview(
                user_id=user_id,
                target_type=target_type,
                target_id=payload.target_id,
                rating=payload.rating,
                body=payload.body,
                image_urls=_dump_meta(meta) if meta else None,
                is_visible=True,
            )
            self.db.add(review)
        else:
            review.rating = payload.rating
            review.body = payload.body
            review.is_visible = True
            current = _parse_meta(review.image_urls)
            review.image_urls = _dump_meta(_meta_with_title(current, payload.title))

        self._mirror_domain_review(
            user_id=user_id,
            target_type=target_type,
            target_id=payload.target_id,
            rating=payload.rating,
            title=payload.title,
            body=payload.body,
        )
        self.db.flush()
        self._recalc_target_ratings(target_type, payload.target_id)
        self.db.commit()
        refreshed = self.repo.get_by_id(review.id)
        assert refreshed is not None
        return self._to_out(refreshed)

    def update_review(
        self,
        *,
        review_id: uuid.UUID,
        user_id: uuid.UUID,
        payload: ReviewUpdate,
    ) -> ReviewOut:
        review = self.repo.get_by_id(review_id)
        if review is None:
            raise NotFoundError("Review not found")
        if review.user_id != user_id:
            raise ForbiddenError("Not your review")
        if payload.rating is not None:
            review.rating = payload.rating
        if payload.body is not None:
            review.body = payload.body
        if payload.title is not None:
            current = _parse_meta(review.image_urls)
            review.image_urls = _dump_meta(_meta_with_title(current, payload.title))
        title = (
            payload.title
            if payload.title is not None
            else _parse_meta(review.image_urls).get("title")
        )
        self._mirror_domain_review(
            user_id=user_id,
            target_type=review.target_type,
            target_id=review.target_id,
            rating=review.rating,
            title=str(title) if title else None,
            body=review.body,
        )
        self.db.flush()
        self._recalc_target_ratings(review.target_type, review.target_id)
        self.db.commit()
        refreshed = self.repo.get_by_id(review.id)
        assert refreshed is not None
        return self._to_out(refreshed)

    def delete_review(self, *, review_id: uuid.UUID, user_id: uuid.UUID) -> None:
        review = self.repo.get_by_id(review_id)
        if review is None:
            raise NotFoundError("Review not found")
        if review.user_id != user_id:
            raise ForbiddenError("Not your review")
        review.is_visible = False
        self.db.flush()
        self._recalc_target_ratings(review.target_type, review.target_id)
        self.db.commit()

    def _ensure_target_exists(self, target_type: str, target_id: uuid.UUID) -> None:
        allowed = {item.value for item in ReviewTargetType} - {"driver"}
        if target_type not in allowed:
            raise ValidationAppError("Unsupported review target")
        found = None
        if target_type == "place":
            found = self.repo.get_place(target_id)
        elif target_type == "hotel":
            found = self.repo.get_hotel(target_id)
        elif target_type == "restaurant":
            found = self.repo.get_restaurant(target_id)
        elif target_type == "guide":
            found = self.repo.get_guide(target_id)
        elif target_type == "activity":
            found = self.repo.get_activity(target_id)
        if found is None:
            raise NotFoundError("Review target not found")

    def _mirror_domain_review(
        self,
        *,
        user_id: uuid.UUID,
        target_type: str,
        target_id: uuid.UUID,
        rating: int,
        title: str | None,
        body: str | None,
    ) -> None:
        if target_type == "place":
            self.repo.upsert_place_review(
                place_id=target_id,
                user_id=user_id,
                rating=rating,
                title=title,
                body=body,
            )
        elif target_type == "hotel":
            self.repo.upsert_hotel_review(
                hotel_id=target_id,
                user_id=user_id,
                rating=rating,
                body=body,
            )

    def _recalc_target_ratings(self, target_type: str, target_id: uuid.UUID) -> None:
        avg, count = self.repo.rating_stats(
            target_type=target_type,
            target_id=target_id,
        )
        rating = Decimal(f"{avg:.2f}")
        if target_type == "place":
            place = self.repo.get_place(target_id)
            if place:
                place.rating_avg = rating
                place.rating_count = count
        elif target_type == "hotel":
            hotel = self.repo.get_hotel(target_id)
            if hotel:
                hotel.rating_avg = rating
                hotel.rating_count = count
        elif target_type == "restaurant":
            restaurant = self.repo.get_restaurant(target_id)
            if restaurant:
                restaurant.rating_avg = rating
                restaurant.rating_count = count
        elif target_type == "guide":
            guide = self.repo.get_guide(target_id)
            if guide:
                guide.rating_avg = rating
                guide.rating_count = count
        elif target_type == "activity":
            activity = self.repo.get_activity(target_id)
            if activity:
                activity.rating_avg = rating
                activity.rating_count = count

    def _to_out(self, review: UserReview) -> ReviewOut:
        meta = _parse_meta(review.image_urls)
        title = meta.get("title")
        return ReviewOut(
            id=review.id,
            target_type=review.target_type,
            target_id=review.target_id,
            user_id=review.user_id,
            rating=review.rating,
            title=str(title) if title else None,
            body=review.body,
            author_name=review.user.full_name if review.user else "Traveller",
            is_visible=review.is_visible,
            is_moderated=review.is_moderated,
            created_at=review.created_at,
            updated_at=review.updated_at,
        )


def _parse_meta(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _dump_meta(meta: dict[str, Any]) -> str | None:
    cleaned = {key: value for key, value in meta.items() if value is not None}
    return json.dumps(cleaned) if cleaned else None


def _meta_with_title(meta: dict[str, Any], title: str | None) -> dict[str, Any]:
    next_meta = dict(meta)
    if title is not None:
        next_meta["title"] = title.strip() or None
    return next_meta
