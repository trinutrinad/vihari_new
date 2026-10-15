"""Review data-access helpers."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    Activity,
    Guide,
    Hotel,
    HotelReview,
    PlaceReview,
    Restaurant,
    TouristPlace,
    UserReview,
)


class ReviewRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_target(
        self,
        *,
        target_type: str,
        target_id: uuid.UUID,
        limit: int = 50,
    ) -> list[UserReview]:
        return list(
            self.db.scalars(
                select(UserReview)
                .where(
                    UserReview.target_type == target_type,
                    UserReview.target_id == target_id,
                    UserReview.is_visible.is_(True),
                )
                .options(selectinload(UserReview.user))
                .order_by(UserReview.created_at.desc())
                .limit(limit),
            ).all(),
        )

    def list_for_user(self, *, user_id: uuid.UUID) -> list[UserReview]:
        return list(
            self.db.scalars(
                select(UserReview)
                .where(UserReview.user_id == user_id)
                .options(selectinload(UserReview.user))
                .order_by(UserReview.created_at.desc()),
            ).all(),
        )

    def get_by_id(self, review_id: uuid.UUID) -> UserReview | None:
        return self.db.scalar(
            select(UserReview)
            .where(UserReview.id == review_id)
            .options(selectinload(UserReview.user)),
        )

    def get_user_review(
        self,
        *,
        user_id: uuid.UUID,
        target_type: str,
        target_id: uuid.UUID,
    ) -> UserReview | None:
        return self.db.scalar(
            select(UserReview)
            .where(
                UserReview.user_id == user_id,
                UserReview.target_type == target_type,
                UserReview.target_id == target_id,
            )
            .options(selectinload(UserReview.user)),
        )

    def rating_stats(
        self,
        *,
        target_type: str,
        target_id: uuid.UUID,
    ) -> tuple[float, int]:
        row = self.db.execute(
            select(
                func.coalesce(func.avg(UserReview.rating), 0),
                func.count(UserReview.id),
            ).where(
                UserReview.target_type == target_type,
                UserReview.target_id == target_id,
                UserReview.is_visible.is_(True),
            ),
        ).one()
        avg = float(row[0] or 0)
        count = int(row[1] or 0)
        return avg, count

    def get_place(self, place_id: uuid.UUID) -> TouristPlace | None:
        return self.db.scalar(
            select(TouristPlace).where(
                TouristPlace.id == place_id,
                TouristPlace.is_deleted.is_(False),
            ),
        )

    def get_hotel(self, hotel_id: uuid.UUID) -> Hotel | None:
        return self.db.scalar(
            select(Hotel).where(Hotel.id == hotel_id, Hotel.is_deleted.is_(False)),
        )

    def get_restaurant(self, restaurant_id: uuid.UUID) -> Restaurant | None:
        return self.db.scalar(
            select(Restaurant).where(
                Restaurant.id == restaurant_id,
                Restaurant.is_deleted.is_(False),
            ),
        )

    def get_guide(self, guide_id: uuid.UUID) -> Guide | None:
        return self.db.scalar(
            select(Guide).where(Guide.id == guide_id, Guide.is_active.is_(True)),
        )

    def get_activity(self, activity_id: uuid.UUID) -> Activity | None:
        return self.db.scalar(
            select(Activity).where(
                Activity.id == activity_id,
                Activity.is_deleted.is_(False),
            ),
        )

    def upsert_place_review(
        self,
        *,
        place_id: uuid.UUID,
        user_id: uuid.UUID,
        rating: int,
        title: str | None,
        body: str | None,
    ) -> None:
        row = self.db.scalar(
            select(PlaceReview).where(
                PlaceReview.place_id == place_id,
                PlaceReview.user_id == user_id,
            ),
        )
        if row is None:
            self.db.add(
                PlaceReview(
                    place_id=place_id,
                    user_id=user_id,
                    rating=rating,
                    title=title,
                    body=body,
                    is_visible=True,
                ),
            )
        else:
            row.rating = rating
            row.title = title
            row.body = body
            row.is_visible = True

    def upsert_hotel_review(
        self,
        *,
        hotel_id: uuid.UUID,
        user_id: uuid.UUID,
        rating: int,
        body: str | None,
    ) -> None:
        row = self.db.scalar(
            select(HotelReview).where(
                HotelReview.hotel_id == hotel_id,
                HotelReview.user_id == user_id,
            ),
        )
        if row is None:
            self.db.add(
                HotelReview(
                    hotel_id=hotel_id,
                    user_id=user_id,
                    rating=rating,
                    body=body,
                    is_visible=True,
                ),
            )
        else:
            row.rating = rating
            row.body = body
            row.is_visible = True
