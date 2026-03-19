import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.payment import Payment, PaymentStatus
from app.models.user import UserRole
from app.repositories.payment_repository import PaymentRepository
from app.repositories.policy_repository import PolicyRepository
from app.schemas.payment import PaymentCreate, PaymentOut


class PaymentService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = PaymentRepository(session)
        self.policy_repo = PolicyRepository(session)

    async def pay_premium(self, data: PaymentCreate, payer_id: int) -> PaymentOut:
        policy = await self.policy_repo.get(data.policy_id)
        if not policy:
            raise NotFoundError("Policy not found")
        if policy.owner_id != payer_id:
            raise ForbiddenError("You do not own this policy")
        payment = Payment(
            transaction_id=f"TXN-{uuid.uuid4().hex[:12].upper()}",
            payer_id=payer_id,
            status=PaymentStatus.completed,  # simplified; hook payment gateway here
            **data.model_dump(),
        )
        created = await self.repo.create(payment)
        return PaymentOut.model_validate(created)

    async def get(self, payment_id: int, user_id: int, role: str) -> PaymentOut:
        payment = await self.repo.get(payment_id)
        if not payment:
            raise NotFoundError("Payment not found")
        if role == UserRole.customer and payment.payer_id != user_id:
            raise ForbiddenError()
        return PaymentOut.model_validate(payment)

    async def list_payments(self, user_id: int, role: str, limit: int, offset: int):
        if role in (UserRole.admin, UserRole.agent):
            payments = await self.repo.list(limit=limit, offset=offset)
        else:
            payments = await self.repo.list_by_payer(user_id, limit=limit, offset=offset)
        return [PaymentOut.model_validate(p) for p in payments]
