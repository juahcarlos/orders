from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from fastapi import HTTPException

from app.core.config import settings
from app.schemas.auth_schemas import TokenPayload, TokenType


class JWTService:
    """Service for managing JWT tokens and password hashing."""
    def __init__(self) -> None:
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_expires = timedelta(minutes=settings.access_token_expire_minutes)
        self.refresh_expires = timedelta(days=settings.refresh_token_expire_days)

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against its hash."""
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )

    def _create_token(
        self,
        user_id: int,
        token_type: TokenType,
        organization_id: int | None = None,
        role: str | None = None,
        expires_delta: timedelta | None = None,
    ) -> str:
        """Generate a single JWT token."""
        expire = datetime.now(UTC) + (
            expires_delta
            or (self.access_expires if token_type == TokenType.ACCESS else self.refresh_expires)
        )
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "type": token_type.value,
            "organization_id": organization_id,
            "role": role,
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_token_pair(
        self,
        user_id: int,
        organization_id: int | None = None,
        role: str | None = None,
    ) -> dict[str, str]:
        """Generate access and refresh token pair."""
        access = self._create_token(user_id, TokenType.ACCESS, organization_id, role)
        refresh = self._create_token(
            user_id, TokenType.REFRESH, organization_id, role, self.refresh_expires
        )
        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
        }

    def verify_token(self, token: str, token_type: TokenType) -> TokenPayload:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != token_type.value:
                raise HTTPException(status_code=401, detail="Invalid token type")
            return TokenPayload(**payload)
        except jwt.PyJWTError as e:
            raise HTTPException(status_code=401, detail="Invalid token") from e
