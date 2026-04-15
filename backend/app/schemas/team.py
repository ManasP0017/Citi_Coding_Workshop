"""Team request / response schemas."""

from typing import Optional
from pydantic import BaseModel, field_validator


class TeamCreate(BaseModel):
    name: str
    location: str = ""
    organization_leader_id: Optional[str] = None
    description: str = ""

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Team name must not be blank")
        return v


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    organization_leader_id: Optional[str] = None
    description: Optional[str] = None


class TeamResponse(BaseModel):
    id: str
    name: str
    location: str
    organization_leader_id: Optional[str]
    description: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
