"""Reservation tests — state machine validation."""
import pytest
from app.services.reservation_service import RESERVATION_TRANSITIONS


def test_reservation_state_transitions():
    """Verify all states have valid transitions."""
    assert "CONFIRMED" in RESERVATION_TRANSITIONS["PENDING"]
    assert "CHECKED_IN" in RESERVATION_TRANSITIONS["CONFIRMED"]
    assert "CHECKED_OUT" in RESERVATION_TRANSITIONS["CHECKED_IN"]
    assert "CANCELLED" in RESERVATION_TRANSITIONS["PENDING"]
    assert "CANCELLED" in RESERVATION_TRANSITIONS["CONFIRMED"]
    # Terminal states
    assert RESERVATION_TRANSITIONS["CHECKED_OUT"] == []
    assert RESERVATION_TRANSITIONS["CANCELLED"] == []
    assert RESERVATION_TRANSITIONS["NO_SHOW"] == []


def test_cannot_checkout_without_checkin():
    """Cannot check out without checking in first."""
    valid_after_pending = RESERVATION_TRANSITIONS["PENDING"]
    assert "CHECKED_OUT" not in valid_after_pending
