from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user_payload
from app.db.session import get_session
from app.schemas.payment import PaymentCreate, PaymentOut
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


def _svc(session: AsyncSession = Depends(get_session)) -> PaymentService:
    return PaymentService(session)


@router.post("/", response_model=PaymentOut, status_code=201)
async def pay_premium(
    data: PaymentCreate,
    payload: dict = Depends(get_current_user_payload),
    svc: PaymentService = Depends(_svc),
):
    return await svc.pay_premium(data, int(payload["sub"]))


@router.get("/", response_model=list[PaymentOut])
async def list_payments(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    payload: dict = Depends(get_current_user_payload),
    svc: PaymentService = Depends(_svc),
):
    return await svc.list_payments(int(payload["sub"]), payload["role"], limit, offset)


@router.get("/{payment_id}", response_model=PaymentOut)
async def get_payment(
    payment_id: int,
    payload: dict = Depends(get_current_user_payload),
    svc: PaymentService = Depends(_svc),
):
    return await svc.get(payment_id, int(payload["sub"]), payload["role"])
