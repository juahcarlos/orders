"""Dependencies for FastAPI: services, repositories, and authentication."""
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.repositories.user import UserRepository
from app.repositories.order import OrderRepository
from app.schemas.auth_schemas import TokenPayload, UserContext
from app.services.auth_service import AuthService
from app.services.jwt_services import JWTService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/auth/token")


def get_jwt_service() -> JWTService:
    """Get JWT service instance."""
    return JWTService()


def get_auth_service(
    db: AsyncSession = Depends(get_db),
    jwt_service: JWTService = Depends(get_jwt_service),
) -> AuthService:
    """Get auth service instance."""
    return AuthService(jwt_service=jwt_service)


async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    """Get user repository instance."""
    return UserRepository(db)

async def get_order_repository(db: AsyncSession = Depends(get_db)) -> OrderRepository:
    """Get order repository instance."""
    return OrderRepository(db)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserContext:
    """Decode JWT and fetch user to ensure authorization."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        token_data = TokenPayload(**payload)
    except InvalidTokenError:
        raise credentials_exception

    if token_data.type != "access":
        raise credentials_exception

    user = await user_repo.get_by_id(int(token_data.sub))
    if not user:
        raise credentials_exception

    return UserContext(
        user_id=user.id,
        email=user.email,
    )


# Annotated dependency для текущего пользователя
CurrentUser = Annotated[UserContext, Depends(get_current_user)]
