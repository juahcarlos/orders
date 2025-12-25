"""Business logic for user authentication and account management."""
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user import UserRepository
from app.schemas.auth_schemas import LoginRequest, TokenPair, UserContext
from app.services.jwt_services import JWTService


class AuthService:
    def __init__(self, jwt_service: JWTService) -> None:
        self.jwt_service = jwt_service

    async def token(
        self,
        request: LoginRequest,
        db: AsyncSession,
    ) -> TokenPair:
        """Verify credentials and issue JWT token pair."""
        user_repo = UserRepository(db)
        user = await user_repo.get_by_email(request.email)

        if not user or not self.jwt_service.verify_password(
            request.password, user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        return self.jwt_service.create_token_pair(user_id=user.id)

    async def register_user(
        self,
        email: str,
        password: str,
        db: AsyncSession,
        **user_data,
    ) -> UserContext:
        """Create a new user after checking for email uniqueness."""
        user_repo = UserRepository(db)

        existing = await user_repo.get_by_email(email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        hashed_password = self.jwt_service.hash_password(password)

        user = await user_repo.create(
            email=email,
            hashed_password=hashed_password,
            **user_data,
        )

        return UserContext(user_id=user.id, email=user.email)
