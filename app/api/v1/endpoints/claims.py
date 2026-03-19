from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user_payload
from app.db.session import get_session
from app.schemas.claim import ClaimCreate, ClaimOut, ClaimStatusUpdate
from app.services.claim_service import ClaimService

router = APIRouter(prefix="/claims", tags=["Claims"])


def _svc(session: AsyncSession = Depends(get_session)) -> ClaimService:
    return ClaimService(session)


@router.post("/", response_model=ClaimOut, status_code=201)
async def create_claim(
    data: ClaimCreate,
    payload: dict = Depends(get_current_user_payload),
    svc: ClaimService = Depends(_svc),
):
    return await svc.create(data, int(payload["sub"]))


@router.get("/", response_model=list[ClaimOut])
async def list_claims(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    payload: dict = Depends(get_current_user_payload),
    svc: ClaimService = Depends(_svc),
):
    return await svc.list_claims(int(payload["sub"]), payload["role"], limit, offset)


@router.get("/{claim_id}", response_model=ClaimOut)
async def get_claim(
    claim_id: int,
    payload: dict = Depends(get_current_user_payload),
    svc: ClaimService = Depends(_svc),
):
    return await svc.get(claim_id, int(payload["sub"]), payload["role"])


@router.patch("/{claim_id}/status", response_model=ClaimOut)
async def update_claim_status(
    claim_id: int,
    data: ClaimStatusUpdate,
    payload: dict = Depends(get_current_user_payload),
    svc: ClaimService = Depends(_svc),
):
    return await svc.update_status(claim_id, data, payload["role"])
