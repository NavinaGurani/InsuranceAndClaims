import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ForbiddenError, BadRequestError
from app.models.claim import Claim, ClaimStatus
from app.models.user import UserRole
from app.repositories.claim_repository import ClaimRepository
from app.repositories.policy_repository import PolicyRepository
from app.schemas.claim import ClaimCreate, ClaimOut, ClaimStatusUpdate

# Valid state machine transitions
ALLOWED_TRANSITIONS: dict[ClaimStatus, list[ClaimStatus]] = {
    ClaimStatus.submitted: [ClaimStatus.under_review],
    ClaimStatus.under_review: [ClaimStatus.approved, ClaimStatus.rejected],
    ClaimStatus.approved: [ClaimStatus.paid],
    ClaimStatus.rejected: [],
    ClaimStatus.paid: [],
}


class ClaimService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = ClaimRepository(session)
        self.policy_repo = PolicyRepository(session)

    async def create(self, data: ClaimCreate, claimant_id: int) -> ClaimOut:
        policy = await self.policy_repo.get(data.policy_id)
        if not policy:
            raise NotFoundError("Policy not found")
        if policy.owner_id != claimant_id:
            raise ForbiddenError("You do not own this policy")
        claim = Claim(
            claim_number=f"CLM-{uuid.uuid4().hex[:10].upper()}",
            claimant_id=claimant_id,
            **data.model_dump(),
        )
        created = await self.repo.create(claim)
        return ClaimOut.model_validate(created)

    async def get(self, claim_id: int, user_id: int, role: str) -> ClaimOut:
        claim = await self.repo.get(claim_id)
        if not claim:
            raise NotFoundError("Claim not found")
        if role == UserRole.customer and claim.claimant_id != user_id:
            raise ForbiddenError()
        return ClaimOut.model_validate(claim)

    async def list_claims(self, user_id: int, role: str, limit: int, offset: int):
        if role in (UserRole.admin, UserRole.agent):
            claims = await self.repo.list(limit=limit, offset=offset)
        else:
            claims = await self.repo.list_by_claimant(user_id, limit=limit, offset=offset)
        return [ClaimOut.model_validate(c) for c in claims]

    async def update_status(self, claim_id: int, data: ClaimStatusUpdate, role: str) -> ClaimOut:
        if role == UserRole.customer:
            raise ForbiddenError("Customers cannot update claim status")
        claim = await self.repo.get(claim_id)
        if not claim:
            raise NotFoundError("Claim not found")
        allowed = ALLOWED_TRANSITIONS.get(claim.status, [])
        if data.status not in allowed:
            raise BadRequestError(f"Cannot transition from {claim.status} to {data.status}")
        claim.status = data.status
        if data.reviewer_notes:
            claim.reviewer_notes = data.reviewer_notes
        updated = await self.repo.update(claim)
        return ClaimOut.model_validate(updated)
