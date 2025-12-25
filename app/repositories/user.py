from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        """Получить пользователя по email."""
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """Проверить существование email."""
        return await self.exists(email=email)

    async def create_user(
        self,
        email: str,
        hashed_password: str,
        name: str,
    ) -> User:
        """Создать нового пользователя."""
        return await self.create(
            email=email,
            hashed_password=hashed_password,
            name=name,
        )
