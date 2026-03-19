from pydantic import BaseModel, Field
from datetime import date, datetime
from decimal import Decimal
from app.models.policy import PolicyType, PolicyStatus


class PolicyCreate(BaseModel):
    policy_type: PolicyType
    coverage_amount: Decimal = Field(gt=0)
    premium_amount: Decimal = Field(gt=0)
    start_date: date
    end_date: date
    description: str | None = None


class PolicyUpdate(BaseModel):
    status: PolicyStatus | None = None
    description: str | None = None


class PolicyOut(BaseModel):
    id: int
    policy_number: str
    owner_id: int
    policy_type: PolicyType
    status: PolicyStatus
    coverage_amount: Decimal
    premium_amount: Decimal
    start_date: date
    end_date: date
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
