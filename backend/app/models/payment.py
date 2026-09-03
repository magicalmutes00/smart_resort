"""Payment model."""
from sqlalchemy import Column, String, DateTime, ForeignKey, UUID, Numeric, Text
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Payment(Base):
    __tablename__ = "payments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"))
    amount = Column(Numeric(12, 2), nullable=False)
    method = Column(String(30), nullable=False)  # CASH, UPI, CARD, ONLINE
    status = Column(String(30), default="PENDING")  # PENDING, COMPLETED, FAILED, REFUNDED
    transaction_reference = Column(String(200))
    provider = Column(String(50))  # INTERNAL, RAZORPAY, etc.
    receipt_url = Column(String(500))
    idempotency_key = Column(String(100), unique=True)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
