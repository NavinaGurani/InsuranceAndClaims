import enum
from sqlalchemy import Column, String, Enum, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.db.base import Base


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"


class PaymentMethod(str, enum.Enum):
    card = "card"
    bank_transfer = "bank_transfer"
    upi = "upi"
    wallet = "wallet"


class Payment(Base):
    __tablename__ = "payments"

    transaction_id = Column(String(100), unique=True, index=True, nullable=False)
    policy_id = Column(ForeignKey("policies.id", ondelete="SET NULL"), nullable=True, index=True)
    payer_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.pending, nullable=False)
    method = Column(Enum(PaymentMethod), nullable=False)
    reference = Column(String(255), nullable=True)  # external gateway reference

    policy = relationship("Policy", back_populates="payments")
    payer = relationship("User", back_populates="payments")
