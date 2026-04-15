"""Achievement request / response schemas."""

from typing import Optional
from pydantic import BaseModel, field_validator

VALID_MONTHS = {
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
}


class AchievementCreate(BaseModel):
    title: str
    description: str = ""
    team_id: str
    month: str
    year: int

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title must not be blank")
        return v

    @field_validator("month")
    @classmethod
    def valid_month(cls, v: str) -> str:
        if v not in VALID_MONTHS:
            raise ValueError(f"Month must be one of {sorted(VALID_MONTHS)}")
        return v

    @field_validator("year")
    @classmethod
    def valid_year(cls, v: int) -> int:
        if not (2000 <= v <= 2100):
            raise ValueError("Year must be between 2000 and 2100")
        return v


class AchievementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    team_id: Optional[str] = None
    month: Optional[str] = None
    year: Optional[int] = None


class AchievementResponse(BaseModel):
    id: str
    title: str
    description: str
    team_id: str
    month: str
    year: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
