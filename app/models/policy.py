import enum
from sqlalchemy import Column, String, Enum, ForeignKey, Numeric, Date, Text
from sqlalchemy.orm import relationship
from app.db.base import Base


class PolicyType(str, enum.Enum):
    health = "health"
    life = "life"
    auto = "auto"
    property = "property"
    travel = "travel"


class PolicyStatus(str, enum.Enum):
    active = "active"
    expired = "expired"
    cancelled = "cancelled"
    pending = "pending"


class Policy(Base):
    __tablename__ = "policies"

    policy_number = Column(String(50), unique=True, index=True, nullable=False)
    owner_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    policy_type = Column(Enum(PolicyType), nullable=False)
    status = Column(Enum(PolicyStatus), default=PolicyStatus.pending, nullable=False)
    coverage_amount = Column(Numeric(15, 2), nullable=False)
    premium_amount = Column(Numeric(10, 2), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)

    owner = relationship("User", back_populates="policies")
    claims = relationship("Claim", back_populates="policy", lazy="selectin")
    payments = relationship("Payment", back_populates="policy", lazy="selectin")
