import enum
from sqlalchemy import Column, String, Enum, ForeignKey, Numeric, Text, Date
from sqlalchemy.orm import relationship
from app.db.base import Base


class ClaimStatus(str, enum.Enum):
    submitted = "submitted"
    under_review = "under_review"
    approved = "approved"
    rejected = "rejected"
    paid = "paid"


class Claim(Base):
    __tablename__ = "claims"

    claim_number = Column(String(50), unique=True, index=True, nullable=False)
    policy_id = Column(ForeignKey("policies.id", ondelete="CASCADE"), nullable=False, index=True)
    claimant_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(Enum(ClaimStatus), default=ClaimStatus.submitted, nullable=False)
    claim_amount = Column(Numeric(15, 2), nullable=False)
    incident_date = Column(Date, nullable=False)
    description = Column(Text, nullable=False)
    reviewer_notes = Column(Text, nullable=True)

    policy = relationship("Policy", back_populates="claims")
    claimant = relationship("User", back_populates="claims")
    documents = relationship("Document", back_populates="claim", lazy="selectin")
