"""Payment service — provider-agnostic abstraction.

Supports: Cash, UPI, Card, Online Payment Gateway (Razorpay/UPI-ready).
All payment secrets stay server-side. Frontend never sees provider credentials.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.payment import Payment


class PaymentMethod(str, Enum):
    CASH = "CASH"
    UPI = "UPI"
    CARD = "CARD"
    ONLINE = "ONLINE"


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"
    REFUND_PENDING = "REFUND_PENDING"


class PaymentProvider(ABC):
    """Abstract payment provider — implement for Razorpay, UPI, etc."""

    @abstractmethod
    def create_payment(self, amount: float, currency: str = "INR", metadata: dict = None) -> dict:
        """Create a payment intent/order. Returns provider-specific response."""
        pass

    @abstractmethod
    def verify_payment(self, transaction_ref: str) -> dict:
        """Verify payment status with provider."""
        pass

    @abstractmethod
    def refund_payment(self, transaction_ref: str, amount: float) -> dict:
        """Initiate refund. Returns provider-specific response."""
        pass


class CashProvider(PaymentProvider):
    """Cash payment — no external provider needed."""

    def create_payment(self, amount: float, currency: str = "INR", metadata: dict = None) -> dict:
        return {
            "provider": "CASH",
            "status": "PENDING",
            "reference": f"CASH-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        }

    def verify_payment(self, transaction_ref: str) -> dict:
        return {"status": "COMPLETED", "reference": transaction_ref}

    def refund_payment(self, transaction_ref: str, amount: float) -> dict:
        return {
            "status": "REFUNDED",
            "reference": transaction_ref,
            "amount": amount,
        }


class UPIProvider(PaymentProvider):
    """UPI payment — integrate with Razorpay, PhonePe, etc.

    To enable: set UPI_PROVIDER=Razorpay and add credentials in .env.
    """

    def __init__(self, api_key: str = "", secret: str = ""):
        self.api_key = api_key
        self.secret = secret
        self.provider = "UPI"

    def create_payment(self, amount: float, currency: str = "INR", metadata: dict = None) -> dict:
        # Placeholder: integrate with Razorpay/UPI gateway
        # razorpay_client = RazorpayClient(auth=(self.api_key, self.secret))
        # response = razorpay_client.payment_link.create({...})
        return {
            "provider": self.provider,
            "status": "PENDING",
            "upi_id": f"smartresort@{metadata.get('upi_id', 'default') if metadata else 'default'}",
            "reference": f"UPI-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "amount": amount,
            "currency": currency,
        }

    def verify_payment(self, transaction_ref: str) -> dict:
        # Placeholder: call provider API to verify
        # In production: razorpay_client.payment.fetch(transaction_ref)
        return {"status": "COMPLETED", "reference": transaction_ref}

    def refund_payment(self, transaction_ref: str, amount: float) -> dict:
        # Placeholder: call provider refund API
        return {
            "status": "REFUNDED",
            "reference": transaction_ref,
            "amount": amount,
        }


class PaymentService:
    """Main payment service using provider abstraction."""

    PROVIDERS = {
        "CASH": CashProvider,
        "UPI": lambda: UPIProvider(
            api_key="",  # Set via env in production
            secret="",
        ),
        "CARD": lambda: UPIProvider(),  # Use same for demo — replace with Stripe
        "ONLINE": lambda: UPIProvider(),  # Generic online
    }

    def __init__(self, db: Session):
        self.db = db

    def _get_provider(self, method: str) -> PaymentProvider:
        """Resolve provider for payment method."""
        provider_cls = self.PROVIDERS.get(method, CashProvider)
        if callable(provider_cls):
            return provider_cls()
        return provider_cls()

    def create_payment(
        self,
        order_id: str,
        amount: float,
        method: str,
        idempotency_key: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Payment:
        """Create a payment record and initiate with provider."""
        # Idempotency
        if idempotency_key:
            existing = self.db.query(Payment).filter(
                Payment.idempotency_key == idempotency_key
            ).first()
            if existing:
                return existing

        # Verify order exists
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("Order not found")

        # Check for existing completed payment
        existing_payment = self.db.query(Payment).filter(
            Payment.order_id == order_id,
            Payment.status == "COMPLETED",
        ).first()
        if existing_payment:
            raise ValueError("Order already paid")

        provider = self._get_provider(method)

        if method == "CASH":
            # Cash: auto-complete
            result = provider.create_payment(amount)
            payment = Payment(
                order_id=order_id,
                amount=amount,
                method=method,
                status="COMPLETED",
                transaction_reference=result["reference"],
                provider="INTERNAL",
            )
        else:
            # Online: create pending, verify separately
            result = provider.create_payment(amount, metadata=metadata)
            payment = Payment(
                order_id=order_id,
                amount=amount,
                method=method,
                status="PENDING",
                transaction_reference=result.get("reference"),
                provider=result.get("provider"),
            )

        payment.idempotency_key = idempotency_key
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def verify_payment(self, payment_id: str) -> Payment:
        """Verify a pending payment with provider and update status."""
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise ValueError("Payment not found")

        if payment.status != "PENDING":
            return payment

        provider = self._get_provider(payment.method)
        result = provider.verify_payment(payment.transaction_reference)

        if result.get("status") == "COMPLETED":
            payment.status = "COMPLETED"
            # Update order status
            order = self.db.query(Order).filter(Order.id == payment.order_id).first()
            if order:
                order.status = "COMPLETED"
        else:
            payment.status = "FAILED"

        self.db.commit()
        self.db.refresh(payment)
        return payment

    def refund_payment(
        self,
        payment_id: str,
        amount: Optional[float] = None,
        reason: Optional[str] = None,
    ) -> Payment:
        """Process a refund."""
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise ValueError("Payment not found")

        if payment.status not in ("COMPLETED", "REFUND_PENDING"):
            raise ValueError("Payment not eligible for refund")

        refund_amount = amount or float(payment.amount)

        provider = self._get_provider(payment.method)
        result = provider.refund_payment(payment.transaction_reference, refund_amount)

        # Record refund
        refund = Payment(
            order_id=payment.order_id,
            amount=-refund_amount,
            method=payment.method,
            status="REFUNDED",
            transaction_reference=f"REFUND-{payment.transaction_reference}",
            provider=payment.provider,
            notes=f"Refund for {payment.id}: {reason}" if reason else f"Refund for {payment.id}",
        )
        self.db.add(refund)

        # Update original
        if refund_amount >= float(payment.amount):
            payment.status = "REFUNDED"
        else:
            payment.status = "PARTIALLY_REFUNDED"

        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get_payment(self, payment_id: str) -> Optional[Payment]:
        return self.db.query(Payment).filter(Payment.id == payment_id).first()
