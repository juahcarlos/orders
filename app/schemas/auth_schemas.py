from enum import Enum

from pydantic import BaseModel, EmailStr


class TokenType(str, Enum):
    """Token types"""

    ACCESS = "access"
    REFRESH = "refresh"


class TokenPayload(BaseModel):
    """Payload of JWT token"""

    sub: str
    exp: int
    type: str


class TokenPair(BaseModel):
    """Pair access/refresh tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserContext(BaseModel):
    user_id: int
    email: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

