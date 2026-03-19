from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.policy import Policy
from app.repositories.base import BaseRepository


class PolicyRepository(BaseRepository[Policy]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Policy, session)

    async def get_by_number(self, number: str) -> Policy | None:
        result = await self.session.execute(select(Policy).where(Policy.policy_number == number))
        return result.scalar_one_or_none()

    async def list_by_owner(self, owner_id: int, limit: int = 100, offset: int = 0):
        result = await self.session.execute(
            select(Policy).where(Policy.owner_id == owner_id).limit(limit).offset(offset)
        )
        return result.scalars().all()
