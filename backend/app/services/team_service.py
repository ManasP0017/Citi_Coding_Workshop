"""Team CRUD business logic."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.team import Team
from app.schemas.team import TeamCreate, TeamUpdate
from app.utils.serializers import model_to_dict


def create_team(req: TeamCreate, db: Session) -> dict:
    team = Team(id=str(uuid.uuid4()), **req.model_dump())
    db.add(team)
    db.commit()
    db.refresh(team)
    return model_to_dict(team)


def list_teams(db: Session, search: Optional[str] = None, location: Optional[str] = None) -> list[dict]:
    q = db.query(Team)
    if search:
        q = q.filter(Team.name.ilike(f"%{search}%") | Team.description.ilike(f"%{search}%"))
    if location:
        q = q.filter(Team.location.ilike(f"%{location}%"))
    return [model_to_dict(t) for t in q.order_by(Team.name).all()]


def get_team(team_id: str, db: Session) -> dict:
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(404, "Team not found")
    return model_to_dict(team)


def update_team(team_id: str, req: TeamUpdate, db: Session) -> dict:
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(404, "Team not found")
    for field, value in req.model_dump(exclude_none=True).items():
        setattr(team, field, value)
    team.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(team)
    return model_to_dict(team)


def delete_team(team_id: str, db: Session) -> None:
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(404, "Team not found")
    db.delete(team)
    db.commit()
