"""Auth request / response schemas."""

from pydantic import BaseModel, EmailStr, field_validator

from app.core.rbac import VALID_ROLES


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = "viewer"

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name must not be blank")
        return v

    @field_validator("role")
    @classmethod
    def valid_role(cls, v: str) -> str:
        if v not in VALID_ROLES:
            raise ValueError(f"Role must be one of {sorted(VALID_ROLES)}")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    token: str


class MeResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
