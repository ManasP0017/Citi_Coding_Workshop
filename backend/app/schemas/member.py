"""Member request / response schemas."""

from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


class MemberCreate(BaseModel):
    name: str
    email: EmailStr
    team_id: Optional[str] = None
    role: str = "member"
    is_team_leader: bool = False
    is_direct_staff: bool = True
    location: str = ""

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name must not be blank")
        return v


class MemberUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    team_id: Optional[str] = None
    role: Optional[str] = None
    is_team_leader: Optional[bool] = None
    is_direct_staff: Optional[bool] = None
    location: Optional[str] = None


class MemberResponse(BaseModel):
    id: str
    name: str
    email: str
    team_id: Optional[str]
    role: str
    is_team_leader: bool
    is_direct_staff: bool
    location: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
