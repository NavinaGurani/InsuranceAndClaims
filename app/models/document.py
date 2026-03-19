from sqlalchemy import Column, String, ForeignKey, Integer, BigInteger
from sqlalchemy.orm import relationship
from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    path = Column(String(500), nullable=False)
    claim_id = Column(ForeignKey("claims.id", ondelete="SET NULL"), nullable=True, index=True)
    uploader_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    claim = relationship("Claim", back_populates="documents")
    uploader = relationship("User", back_populates="documents")
