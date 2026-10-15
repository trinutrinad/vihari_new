"""Transport data-access helpers."""

from __future__ import annotations

import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import TransportOption


class TransportRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _base_query(self):
        return select(TransportOption).where(TransportOption.is_active.is_(True))

    def list_options(
        self,
        *,
        page: int,
        page_size: int,
        q: str | None = None,
        vehicle_type: str | None = None,
        max_base_fare: int | None = None,
    ) -> tuple[list[TransportOption], int]:
        query = self._base_query()
        if q:
            like = f"%{q.strip()}%"
            query = query.where(
                or_(
                    TransportOption.name.ilike(like),
                    TransportOption.code.ilike(like),
                    TransportOption.vehicle_type.ilike(like),
                    TransportOption.description.ilike(like),
                ),
            )
        if vehicle_type:
            query = query.where(
                TransportOption.vehicle_type == vehicle_type.strip().lower(),
            )
        if max_base_fare is not None:
            query = query.where(TransportOption.base_fare_inr <= max_base_fare)

        count_query = select(func.count()).select_from(query.order_by(None).subquery())
        total = int(self.db.scalar(count_query) or 0)
        rows = self.db.scalars(
            query.order_by(
                TransportOption.base_fare_inr.asc(),
                TransportOption.name.asc(),
            )
            .offset((page - 1) * page_size)
            .limit(page_size),
        ).all()
        return list(rows), total

    def get_by_id(self, option_id: uuid.UUID) -> TransportOption | None:
        return self.db.scalar(self._base_query().where(TransportOption.id == option_id))

    def get_by_code(self, code: str) -> TransportOption | None:
        return self.db.scalar(
            self._base_query().where(TransportOption.code == code.strip().lower()),
        )
