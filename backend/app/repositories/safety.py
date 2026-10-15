"""Safety / emergency-contact data access."""

from __future__ import annotations

import uuid

from sqlalchemy import or_, select, update
from sqlalchemy.orm import Session

from app.models import City, EmergencyContact, SupportTicket


class SafetyRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def find_city(self, city_slug_or_name: str) -> City | None:
        key = city_slug_or_name.strip()
        if not key:
            return None
        return self.db.scalar(
            select(City).where(
                or_(City.slug == key.lower(), City.name.ilike(key)),
            ),
        )

    def list_contacts(self, *, user_id: uuid.UUID) -> list[EmergencyContact]:
        return list(
            self.db.scalars(
                select(EmergencyContact)
                .where(EmergencyContact.user_id == user_id)
                .order_by(
                    EmergencyContact.is_primary.desc(),
                    EmergencyContact.created_at.asc(),
                ),
            ).all(),
        )

    def get_contact(
        self,
        *,
        contact_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> EmergencyContact | None:
        return self.db.scalar(
            select(EmergencyContact).where(
                EmergencyContact.id == contact_id,
                EmergencyContact.user_id == user_id,
            ),
        )

    def clear_primary(self, *, user_id: uuid.UUID) -> None:
        self.db.execute(
            update(EmergencyContact)
            .where(
                EmergencyContact.user_id == user_id,
                EmergencyContact.is_primary.is_(True),
            )
            .values(is_primary=False),
        )

    def add_contact(self, contact: EmergencyContact) -> EmergencyContact:
        self.db.add(contact)
        self.db.flush()
        return contact

    def add_ticket(self, ticket: SupportTicket) -> SupportTicket:
        self.db.add(ticket)
        self.db.flush()
        return ticket
