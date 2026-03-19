from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserRegister, TokenOut, UserOut


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = UserRepository(session)

    async def register(self, data: UserRegister) -> UserOut:
        if await self.repo.get_by_email(data.email):
            raise ConflictError("Email already registered")
        user = User(
            email=data.email,
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
            role=data.role,
        )
        created = await self.repo.create(user)
        return UserOut.model_validate(created)

    async def login(self, email: str, password: str) -> TokenOut:
        user = await self.repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid credentials")
        if not user.is_active:
            raise UnauthorizedError("Account is disabled")
        token = create_access_token(user.id, extra={"role": user.role.value, "email": user.email})
        return TokenOut(access_token=token, user=UserOut.model_validate(user))
