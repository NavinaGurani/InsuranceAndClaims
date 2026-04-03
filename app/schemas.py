"""Pydantic schemas for request validation and response serialization."""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


# ── Enums (plain strings — no DB enum needed) ───────────────────────────────────
UserRole        = str  # "admin" | "agent" | "customer"
PolicyType      = str  # "health" | "life" | "auto" | "property" | "travel"
PolicyStatus    = str  # "active" | "expired" | "cancelled" | "pending"
ClaimStatus     = str  # "submitted" | "under_review" | "approved" | "rejected" | "paid"
PaymentStatus   = str  # "pending" | "completed" | "failed" | "refunded"
PaymentMethod   = str  # "card" | "bank_transfer" | "upi" | "wallet"


# ── User ───────────────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = "customer"


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime


# ── Policy ─────────────────────────────────────────────────────────────────────
class PolicyCreate(BaseModel):
    policy_type: PolicyType
    coverage_amount: float
    premium_amount: float
    start_date: date
    end_date: date
    description: Optional[str] = None


class PolicyUpdate(BaseModel):
    status: Optional[PolicyStatus] = None
    description: Optional[str] = None


class PolicyOut(BaseModel):
    id: int
    policy_number: str
    owner_id: int
    policy_type: PolicyType
    status: PolicyStatus
    coverage_amount: float
    premium_amount: float
    start_date: date
    end_date: date
    description: Optional[str]
    created_at: datetime


# ── Claim ──────────────────────────────────────────────────────────────────────
class ClaimCreate(BaseModel):
    policy_id: int
    claim_amount: float
    incident_date: date
    description: str


class ClaimStatusUpdate(BaseModel):
    status: ClaimStatus
    reviewer_notes: Optional[str] = None


class ClaimOut(BaseModel):
    id: int
    claim_number: str
    policy_id: int
    claimant_id: int
    status: ClaimStatus
    claim_amount: float
    incident_date: date
    description: str
    reviewer_notes: Optional[str]
    created_at: datetime


# ── Payment ────────────────────────────────────────────────────────────────────
class PaymentCreate(BaseModel):
    policy_id: int
    amount: float
    method: PaymentMethod


class PaymentOut(BaseModel):
    id: int
    transaction_id: str
    policy_id: int
    payer_id: int
    amount: float
    status: PaymentStatus
    method: PaymentMethod
    reference: Optional[str]
    created_at: datetime


# ── Triage ─────────────────────────────────────────────────────────────────────
class TriageResult(BaseModel):
    claim_id: int
    risk_score: float
    flag: str          # "low" | "medium" | "high"
    reasons: list[str]
