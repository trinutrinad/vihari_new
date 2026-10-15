"""Safety tips, emergency contacts, and mock SOS."""

from __future__ import annotations

import secrets
import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import EmergencyContact, SupportTicket
from app.repositories.safety import SafetyRepository
from app.schemas.safety import (
    EmergencyContactCreate,
    EmergencyContactOut,
    EmergencyContactUpdate,
    EmergencyNumberOut,
    SafetyHintOut,
    SafetyTipsOut,
    SosOut,
    SosRequest,
)

GENERAL_TIPS = [
    "Share your itinerary and live location with a trusted contact.",
    "Prefer registered taxis or ride apps for late-night travel.",
    "Keep offline copies of ID and emergency numbers on your phone.",
    "Follow local advisories for weather, crowds, and restricted areas.",
    "Avoid isolated shortcuts after dark in unfamiliar neighbourhoods.",
]

INDIA_EMERGENCY_NUMBERS = [
    EmergencyNumberOut(
        label="National emergency",
        number="112",
        notes="Single emergency number for police, fire, and ambulance.",
    ),
    EmergencyNumberOut(
        label="Police",
        number="100",
        notes="Legacy police helpline; 112 is preferred where available.",
    ),
    EmergencyNumberOut(
        label="Fire",
        number="101",
        notes="Fire and rescue.",
    ),
    EmergencyNumberOut(
        label="Ambulance",
        number="102",
        notes="Medical emergency / ambulance.",
    ),
    EmergencyNumberOut(
        label="Women helpline",
        number="1091",
        notes="Women's helpline (availability varies by state).",
    ),
    EmergencyNumberOut(
        label="Tourist helpline",
        number="1363",
        notes="Tourist helpline — confirm locally for current coverage.",
    ),
]


class SafetyService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = SafetyRepository(db)

    def get_tips(self, *, city: str | None = None) -> SafetyTipsOut:
        city_name: str | None = None
        tips = list(GENERAL_TIPS)
        hints: list[SafetyHintOut] = []

        if city:
            row = self.repo.find_city(city)
            city_name = row.name if row else city.strip().title()
            tips = [
                f"In {city_name}, keep hotel/guesthouse address saved offline.",
                f"Ask locals or your stay about safer routes around {city_name}.",
                *GENERAL_TIPS[:3],
            ]
            hints = [
                SafetyHintOut(
                    kind="hospital",
                    name=f"Hospitals near {city_name} (unverified)",
                    note="Confirm on a live map before relying on this hint.",
                ),
                SafetyHintOut(
                    kind="police",
                    name=f"Police assistance near {city_name} (unverified)",
                    note="Dial 112 in an emergency — do not rely on demo map pins.",
                ),
                SafetyHintOut(
                    kind="petrol_pump",
                    name=f"Fuel stations near {city_name} (unverified)",
                    note="Availability varies — check a live map.",
                ),
            ]

        return SafetyTipsOut(
            city=city_name,
            tips=tips,
            nearby_hints=hints,
            emergency_numbers=list(INDIA_EMERGENCY_NUMBERS),
        )

    def list_emergency_numbers(self) -> list[EmergencyNumberOut]:
        return list(INDIA_EMERGENCY_NUMBERS)

    def list_contacts(self, *, user_id: uuid.UUID) -> list[EmergencyContactOut]:
        return [self._to_contact(row) for row in self.repo.list_contacts(user_id=user_id)]

    def create_contact(
        self,
        *,
        user_id: uuid.UUID,
        payload: EmergencyContactCreate,
    ) -> EmergencyContactOut:
        if payload.is_primary:
            self.repo.clear_primary(user_id=user_id)
        contact = EmergencyContact(
            user_id=user_id,
            name=payload.name.strip(),
            phone=payload.phone.strip(),
            relationship_label=(
                payload.relationship_label.strip() if payload.relationship_label else None
            ),
            is_primary=payload.is_primary,
        )
        self.repo.add_contact(contact)
        self.db.commit()
        self.db.refresh(contact)
        return self._to_contact(contact)

    def update_contact(
        self,
        *,
        contact_id: uuid.UUID,
        user_id: uuid.UUID,
        payload: EmergencyContactUpdate,
    ) -> EmergencyContactOut:
        contact = self.repo.get_contact(contact_id=contact_id, user_id=user_id)
        if contact is None:
            raise NotFoundError("Emergency contact not found")
        if payload.is_primary:
            self.repo.clear_primary(user_id=user_id)
            contact.is_primary = True
        elif payload.is_primary is False:
            contact.is_primary = False
        if payload.name is not None:
            contact.name = payload.name.strip()
        if payload.phone is not None:
            contact.phone = payload.phone.strip()
        if payload.relationship_label is not None:
            contact.relationship_label = payload.relationship_label.strip() or None
        self.db.commit()
        self.db.refresh(contact)
        return self._to_contact(contact)

    def delete_contact(self, *, contact_id: uuid.UUID, user_id: uuid.UUID) -> None:
        contact = self.repo.get_contact(contact_id=contact_id, user_id=user_id)
        if contact is None:
            raise NotFoundError("Emergency contact not found")
        self.db.delete(contact)
        self.db.commit()

    def create_sos(self, *, user_id: uuid.UUID, payload: SosRequest) -> SosOut:
        stamp = datetime.now(UTC).strftime("%Y%m%d")
        ticket_number = f"SOS-{stamp}-{secrets.token_hex(3).upper()}"
        location_bits = []
        if payload.city:
            location_bits.append(f"city={payload.city}")
        if payload.latitude is not None and payload.longitude is not None:
            location_bits.append(f"lat={payload.latitude},lng={payload.longitude}")
        body = payload.message or "Mock SOS triggered from Bharat Yatra app."
        if location_bits:
            body = f"{body}\nLocation: {'; '.join(location_bits)}"
        body = (
            f"{body}\n\n[MOCK] This ticket does not alert real emergency services. "
            "Dial 112 for real emergencies."
        )
        ticket = SupportTicket(
            user_id=user_id,
            ticket_number=ticket_number,
            subject="Mock SOS alert",
            body=body,
            status="open",
            priority="urgent",
        )
        self.repo.add_ticket(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        from app.services.notify import notify_user

        notify_user(
            self.db,
            user_id=user_id,
            title="Mock SOS recorded",
            body=f"{ticket.ticket_number} — demo only. Dial 112 for real emergencies.",
            category="safety",
            payload={
                "ticket_id": str(ticket.id),
                "href": "/safety",
            },
        )
        return SosOut(
            ticket_id=ticket.id,
            ticket_number=ticket.ticket_number,
            status=ticket.status,
            message=(
                "Mock SOS recorded. This does not contact police or ambulance — "
                "dial 112 if you need real help."
            ),
        )

    def _to_contact(self, contact: EmergencyContact) -> EmergencyContactOut:
        return EmergencyContactOut(
            id=contact.id,
            name=contact.name,
            phone=contact.phone,
            relationship_label=contact.relationship_label,
            is_primary=contact.is_primary,
        )
