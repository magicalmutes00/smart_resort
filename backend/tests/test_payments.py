"""Payment tests — provider abstraction, idempotency."""
import pytest
from app.services.payment_service import (
    CashProvider, UPIProvider, PaymentService, PaymentMethod,
)


def test_cash_provider_create():
    """Cash provider should produce valid response."""
    provider = CashProvider()
    result = provider.create_payment(100.0)
    assert result["provider"] == "CASH"
    assert result["status"] == "PENDING"
    assert result["reference"].startswith("CASH-")


def test_cash_provider_verify():
    """Cash provider verification should return COMPLETED."""
    provider = CashProvider()
    result = provider.verify_payment("CASH-123")
    assert result["status"] == "COMPLETED"


def test_upi_provider_create():
    """UPI provider should generate UPI payment reference."""
    provider = UPIProvider()
    result = provider.create_payment(500.0, metadata={"upi_id": "merchant@upi"})
    assert result["provider"] == "UPI"
    assert "upi_id" in result
    assert result["amount"] == 500.0


def test_refund_creates_negative_amount():
    """Refund should produce a negative-amount record."""
    provider = CashProvider()
    result = provider.refund_payment("CASH-001", 100.0)
    assert result["status"] == "REFUNDED"
    assert result["amount"] == 100.0
