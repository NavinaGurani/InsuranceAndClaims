import enum
from sqlalchemy import Column, String, Enum, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    agent = "agent"
    customer = "customer"


class User(Base):
    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.customer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    policies = relationship("Policy", back_populates="owner", lazy="selectin")
    claims = relationship("Claim", back_populates="claimant", lazy="selectin")
    payments = relationship("Payment", back_populates="payer", lazy="selectin")
    documents = relationship("Document", back_populates="uploader", lazy="selectin")
