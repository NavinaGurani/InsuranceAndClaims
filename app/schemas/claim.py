from pydantic import BaseModel, Field
from datetime import date, datetime
from decimal import Decimal
from app.models.claim import ClaimStatus


class ClaimCreate(BaseModel):
    policy_id: int
    claim_amount: Decimal = Field(gt=0)
    incident_date: date
    description: str = Field(min_length=10)


class ClaimStatusUpdate(BaseModel):
    status: ClaimStatus
    reviewer_notes: str | None = None


class ClaimOut(BaseModel):
    id: int
    claim_number: str
    policy_id: int
    claimant_id: int
    status: ClaimStatus
    claim_amount: Decimal
    incident_date: date
    description: str
    reviewer_notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
