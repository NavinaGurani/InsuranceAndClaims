from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user_payload, get_current_user_id
from app.db.session import get_session
from app.schemas.policy import PolicyCreate, PolicyOut, PolicyUpdate
from app.services.policy_service import PolicyService

router = APIRouter(prefix="/policies", tags=["Policies"])


def _svc(session: AsyncSession = Depends(get_session)) -> PolicyService:
    return PolicyService(session)


@router.post("/", response_model=PolicyOut, status_code=201)
async def create_policy(
    data: PolicyCreate,
    payload: dict = Depends(get_current_user_payload),
    svc: PolicyService = Depends(_svc),
):
    return await svc.create(data, int(payload["sub"]))


@router.get("/", response_model=list[PolicyOut])
async def list_policies(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    payload: dict = Depends(get_current_user_payload),
    svc: PolicyService = Depends(_svc),
):
    return await svc.list_policies(int(payload["sub"]), payload["role"], limit, offset)


@router.get("/{policy_id}", response_model=PolicyOut)
async def get_policy(
    policy_id: int,
    payload: dict = Depends(get_current_user_payload),
    svc: PolicyService = Depends(_svc),
):
    return await svc.get(policy_id, int(payload["sub"]), payload["role"])


@router.patch("/{policy_id}", response_model=PolicyOut)
async def update_policy(
    policy_id: int,
    data: PolicyUpdate,
    payload: dict = Depends(get_current_user_payload),
    svc: PolicyService = Depends(_svc),
):
    return await svc.update(policy_id, data, payload["role"])
