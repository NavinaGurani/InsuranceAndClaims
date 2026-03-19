from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.payment import Payment
from app.repositories.base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Payment, session)

    async def get_by_transaction(self, txn_id: str) -> Payment | None:
        result = await self.session.execute(select(Payment).where(Payment.transaction_id == txn_id))
        return result.scalar_one_or_none()

    async def list_by_payer(self, payer_id: int, limit: int = 100, offset: int = 0):
        result = await self.session.execute(
            select(Payment).where(Payment.payer_id == payer_id).limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def list_by_policy(self, policy_id: int):
        result = await self.session.execute(select(Payment).where(Payment.policy_id == policy_id))
        return result.scalars().all()
