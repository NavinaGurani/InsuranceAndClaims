import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.policy import Policy
from app.models.user import UserRole
from app.repositories.policy_repository import PolicyRepository
from app.schemas.policy import PolicyCreate, PolicyOut, PolicyUpdate


class PolicyService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = PolicyRepository(session)

    async def create(self, data: PolicyCreate, owner_id: int) -> PolicyOut:
        policy = Policy(
            policy_number=f"POL-{uuid.uuid4().hex[:10].upper()}",
            owner_id=owner_id,
            **data.model_dump(),
        )
        created = await self.repo.create(policy)
        return PolicyOut.model_validate(created)

    async def get(self, policy_id: int, user_id: int, role: str) -> PolicyOut:
        policy = await self.repo.get(policy_id)
        if not policy:
            raise NotFoundError("Policy not found")
        if role == UserRole.customer and policy.owner_id != user_id:
            raise ForbiddenError()
        return PolicyOut.model_validate(policy)

    async def list_policies(self, user_id: int, role: str, limit: int, offset: int):
        if role in (UserRole.admin, UserRole.agent):
            policies = await self.repo.list(limit=limit, offset=offset)
        else:
            policies = await self.repo.list_by_owner(user_id, limit=limit, offset=offset)
        return [PolicyOut.model_validate(p) for p in policies]

    async def update(self, policy_id: int, data: PolicyUpdate, role: str) -> PolicyOut:
        if role == UserRole.customer:
            raise ForbiddenError()
        policy = await self.repo.get(policy_id)
        if not policy:
            raise NotFoundError("Policy not found")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(policy, field, value)
        updated = await self.repo.update(policy)
        return PolicyOut.model_validate(updated)
