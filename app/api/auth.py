"""Authentication API endpoints for user registration and JWT token management."""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_auth_service, get_db
from app.schemas.auth_schemas import LoginRequest, RegisterRequest, TokenPair, UserContext
from app.services.auth_service import AuthService
from app.utils.limiter import limiter


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserContext, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.register_limit)
async def register(
    request: Request,
    data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
    db: AsyncSession = Depends(get_db),
) -> UserContext:
    """Register a new user and return public user context."""
    return await auth_service.register_user(
        email=data.email,
        password=data.password,
        db=db,
    )


@router.post("/token", response_model=TokenPair)
@limiter.limit(settings.token_limit)
async def token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
    db: AsyncSession = Depends(get_db),
) -> TokenPair:
    """Authenticate user and return access/refresh token pair."""
    request = LoginRequest(email=form_data.username, password=form_data.password)

    try:
        tokens = await auth_service.token(request=request, db=db)
        return tokens
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
