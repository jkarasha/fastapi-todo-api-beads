from datetime import datetime

from pydantic import EmailStr, Field

from src.core.schemas import BaseSchema


class UserCreate(BaseSchema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseSchema):
    id: int
    email: EmailStr
    created_at: datetime


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str


class TokenResponse(BaseSchema):
    access_token: str
    token_type: str = "bearer"
