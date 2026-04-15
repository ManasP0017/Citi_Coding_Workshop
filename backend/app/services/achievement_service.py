"""Achievement CRUD business logic."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.achievement import Achievement
from app.models.team import Team
from app.schemas.achievement import AchievementCreate, AchievementUpdate
from app.utils.serializers import model_to_dict


def create_achievement(req: AchievementCreate, db: Session) -> dict:
    if not db.query(Team).filter(Team.id == req.team_id).first():
        raise HTTPException(404, "Team not found")
    achievement = Achievement(id=str(uuid.uuid4()), **req.model_dump())
    db.add(achievement)
    db.commit()
    db.refresh(achievement)
    return model_to_dict(achievement)


def list_achievements(
    db: Session,
    search: Optional[str] = None,
    team_id: Optional[str] = None,
    month: Optional[str] = None,
    year: Optional[int] = None,
) -> list[dict]:
    q = db.query(Achievement)
    if search:
        q = q.filter(
            Achievement.title.ilike(f"%{search}%")
            | Achievement.description.ilike(f"%{search}%")
        )
    if team_id:
        q = q.filter(Achievement.team_id == team_id)
    if month:
        q = q.filter(Achievement.month == month)
    if year:
        q = q.filter(Achievement.year == year)
    return [
        model_to_dict(a)
        for a in q.order_by(Achievement.year.desc(), Achievement.month.desc()).all()
    ]


def get_achievement(achievement_id: str, db: Session) -> dict:
    achievement = db.query(Achievement).filter(Achievement.id == achievement_id).first()
    if not achievement:
        raise HTTPException(404, "Achievement not found")
    return model_to_dict(achievement)


def update_achievement(achievement_id: str, req: AchievementUpdate, db: Session) -> dict:
    achievement = db.query(Achievement).filter(Achievement.id == achievement_id).first()
    if not achievement:
        raise HTTPException(404, "Achievement not found")
    for field, value in req.model_dump(exclude_none=True).items():
        setattr(achievement, field, value)
    achievement.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(achievement)
    return model_to_dict(achievement)


def delete_achievement(achievement_id: str, db: Session) -> None:
    achievement = db.query(Achievement).filter(Achievement.id == achievement_id).first()
    if not achievement:
        raise HTTPException(404, "Achievement not found")
    db.delete(achievement)
    db.commit()
