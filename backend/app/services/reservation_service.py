"""Reservation service with state machine."""
from datetime import date, datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.models.reservation import Reservation, GuestFolio, FolioItem
from app.models.staff import Guest
from app.models.rooms import Room


RESERVATION_TRANSITIONS = {
    "PENDING": ["CONFIRMED", "CANCELLED"],
    "CONFIRMED": ["CHECKED_IN", "CANCELLED", "NO_SHOW"],
    "CHECKED_IN": ["CHECKED_OUT"],
    "CHECKED_OUT": [],
    "CANCELLED": [],
    "NO_SHOW": [],
}


class ReservationService:
    """Manage reservation lifecycle and guest folios."""

    def __init__(self, db: Session):
        self.db = db

    def create_reservation(
        self,
        guest_id: str,
        room_id: str,
        check_in: date,
        check_out: date,
        property_id: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Reservation:
        """Create a new reservation in PENDING state."""
        if check_in >= check_out:
            raise ValueError("check_out must be after check_in")

        nights = (check_out - check_in).days

        # Get room price
        room = self.db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise ValueError("Room not found")

        # Get room type price (in real app use a join)
        total_amount = float(nights * 3500)  # Default rate

        reservation = Reservation(
            property_id=property_id,
            guest_id=guest_id,
            room_id=room_id,
            check_in=check_in,
            check_out=check_out,
            status="PENDING",
            total_amount=total_amount,
            notes=notes,
        )
        self.db.add(reservation)
        self.db.commit()
        self.db.refresh(reservation)

        # Auto-create folio
        folio = GuestFolio(
            reservation_id=reservation.id,
            guest_id=guest_id,
            room_id=room_id,
            total_charges=0,
            paid_amount=0,
            status="OPEN",
        )
        self.db.add(folio)
        self.db.commit()

        return reservation

    def confirm(self, reservation_id: str) -> Reservation:
        return self._transition(reservation_id, "CONFIRMED")

    def check_in(self, reservation_id: str) -> Reservation:
        res = self._transition(reservation_id, "CHECKED_IN")
        # Mark room as OCCUPIED
        room = self.db.query(Room).filter(Room.id == res.room_id).first()
        if room:
            room.status = "OCCUPIED"
            self.db.commit()
        return res

    def check_out(self, reservation_id: str) -> Reservation:
        res = self._transition(reservation_id, "CHECKED_OUT")
        # Auto-create housekeeping task
        from app.models.housekeeping import HousekeepingTask
        hk = HousekeepingTask(
            room_id=res.room_id,
            task_type="CLEANING",
            priority="NORMAL",
            status="PENDING",
            notes=f"Post-checkout cleaning for room",
        )
        self.db.add(hk)
        # Mark room for cleaning
        room = self.db.query(Room).filter(Room.id == res.room_id).first()
        if room:
            room.status = "CLEANING"
        self.db.commit()
        return res

    def cancel(self, reservation_id: str) -> Reservation:
        return self._transition(reservation_id, "CANCELLED")

    def mark_no_show(self, reservation_id: str) -> Reservation:
        return self._transition(reservation_id, "NO_SHOW")

    def _transition(self, reservation_id: str, new_status: str) -> Reservation:
        reservation = self.db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if not reservation:
            raise ValueError("Reservation not found")

        valid = RESERVATION_TRANSITIONS.get(reservation.status, [])
        if new_status not in valid:
            raise ValueError(f"Invalid transition: {reservation.status} → {new_status}")

        reservation.status = new_status
        self.db.commit()
        self.db.refresh(reservation)
        return reservation

    def add_folio_charge(
        self,
        reservation_id: str,
        item_type: str,
        description: str,
        amount: float,
        reference_id: Optional[str] = None,
    ) -> FolioItem:
        """Add a charge to the guest folio (e.g. from a room service order)."""
        folio = self.db.query(GuestFolio).filter(
            GuestFolio.reservation_id == reservation_id,
            GuestFolio.status == "OPEN",
        ).first()
        if not folio:
            raise ValueError("Open folio not found for reservation")

        item = FolioItem(
            folio_id=folio.id,
            item_type=item_type,
            description=description,
            amount=amount,
            reference_id=reference_id,
        )
        self.db.add(item)
        folio.total_charges = (folio.total_charges or 0) + amount
        self.db.commit()
        self.db.refresh(item)
        return item

    def settle_folio(
        self,
        reservation_id: str,
        payment_amount: float,
    ) -> GuestFolio:
        """Settle folio on checkout."""
        folio = self.db.query(GuestFolio).filter(
            GuestFolio.reservation_id == reservation_id,
        ).first()
        if not folio:
            raise ValueError("Folio not found")

        folio.paid_amount = (folio.paid_amount or 0) + payment_amount
        if folio.paid_amount >= (folio.total_charges or 0):
            folio.status = "SETTLED"
        self.db.commit()
        self.db.refresh(folio)
        return folio
