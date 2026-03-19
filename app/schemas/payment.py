from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from app.models.payment import PaymentStatus, PaymentMethod


class PaymentCreate(BaseModel):
    policy_id: int
    amount: Decimal = Field(gt=0)
    method: PaymentMethod


class PaymentOut(BaseModel):
    id: int
    transaction_id: str
    policy_id: int | None
    payer_id: int
    amount: Decimal
    status: PaymentStatus
    method: PaymentMethod
    reference: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
