from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.claim import Claim, ClaimStatus
from app.repositories.base import BaseRepository


class ClaimRepository(BaseRepository[Claim]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Claim, session)

    async def get_by_number(self, number: str) -> Claim | None:
        result = await self.session.execute(select(Claim).where(Claim.claim_number == number))
        return result.scalar_one_or_none()

    async def list_by_claimant(self, claimant_id: int, limit: int = 100, offset: int = 0):
        result = await self.session.execute(
            select(Claim).where(Claim.claimant_id == claimant_id).limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def list_by_policy(self, policy_id: int):
        result = await self.session.execute(select(Claim).where(Claim.policy_id == policy_id))
        return result.scalars().all()
