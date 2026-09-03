"""Payments routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Header, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID

from app.core.database import get_db
from app.core.rbac import RequirePermission
from app.services.payment_service import PaymentService

router = APIRouter()


class PaymentCreate(BaseModel):
    order_id: UUID
    amount: float
    method: str = "CASH"
    metadata: Optional[dict] = None


class PaymentResponse(BaseModel):
    id: UUID
    order_id: UUID
    amount: float
    method: str
    status: str
    transaction_reference: Optional[str]
    provider: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


@router.post("/", response_model=dict, status_code=201)
async def create_payment(
    payment_data: PaymentCreate,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current: dict = Depends(RequirePermission("payments.create")),
):
    """Create a payment for an order."""
    svc = PaymentService(db)
    try:
        payment = svc.create_payment(
            order_id=str(payment_data.order_id),
            amount=payment_data.amount,
            method=payment_data.method,
            idempotency_key=idempotency_key,
            metadata=payment_data.metadata,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "id": str(payment.id),
        "order_id": str(payment.order_id),
        "amount": float(payment.amount),
        "method": payment.method,
        "status": payment.status,
        "transaction_reference": payment.transaction_reference,
    }


@router.get("/{payment_id}", response_model=dict)
def get_payment(
    payment_id: UUID,
    db: Session = Depends(get_db),
    current: dict = Depends(RequirePermission("payments.read")),
):
    """Get payment details."""
    svc = PaymentService(db)
    payment = svc.get_payment(str(payment_id))
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {
        "id": str(payment.id),
        "order_id": str(payment.order_id),
        "amount": float(payment.amount),
        "method": payment.method,
        "status": payment.status,
        "transaction_reference": payment.transaction_reference,
        "created_at": payment.created_at.isoformat() if payment.created_at else None,
    }


@router.post("/{payment_id}/verify", response_model=dict)
async def verify_payment(
    payment_id: UUID,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current: dict = Depends(RequirePermission("payments.verify")),
):
    """Verify a pending payment with the provider."""
    svc = PaymentService(db)
    try:
        payment = svc.verify_payment(str(payment_id))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"id": str(payment.id), "status": payment.status}


@router.post("/{payment_id}/refund", response_model=dict)
def refund_payment(
    payment_id: UUID,
    amount: Optional[float] = Query(None),
    reason: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current: dict = Depends(RequirePermission("payments.refund")),
):
    """Refund a payment."""
    svc = PaymentService(db)
    try:
        payment = svc.refund_payment(str(payment_id), amount=amount, reason=reason)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"id": str(payment.id), "status": payment.status, "amount": float(payment.amount)}
