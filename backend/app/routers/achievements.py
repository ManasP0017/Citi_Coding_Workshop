"""Achievements CRUD routes."""

from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_user, CanWrite, CanDelete
from app.core.broadcaster import broadcast
from app.schemas.achievement import AchievementCreate, AchievementUpdate
from app.schemas.common import MessageResponse, CreatedResponse
from app.services import achievement_service

router = APIRouter(prefix="/api/achievements", tags=["achievements"])


@router.post("", status_code=201)
async def create_achievement(
    req: AchievementCreate,
    db: Session = Depends(get_db),
    _=Depends(CanWrite()),
):
    data = achievement_service.create_achievement(req, db)
    await broadcast("achievement.created", "achievement", data)
    return CreatedResponse(message="Achievement created successfully", id=data["id"])


@router.get("")
def get_achievements(
    search: Optional[str] = None,
    team_id: Optional[str] = None,
    month: Optional[str] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return {"achievements": achievement_service.list_achievements(db, search, team_id, month, year)}


@router.get("/{achievement_id}")
def get_achievement(
    achievement_id: str,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return achievement_service.get_achievement(achievement_id, db)


@router.put("/{achievement_id}")
async def update_achievement(
    achievement_id: str,
    req: AchievementUpdate,
    db: Session = Depends(get_db),
    _=Depends(CanWrite()),
):
    data = achievement_service.update_achievement(achievement_id, req, db)
    await broadcast("achievement.updated", "achievement", data)
    return MessageResponse(message="Achievement updated successfully")


@router.delete("/{achievement_id}", status_code=204)
async def delete_achievement(
    achievement_id: str,
    db: Session = Depends(get_db),
    _=Depends(CanDelete()),
):
    achievement_service.delete_achievement(achievement_id, db)
    await broadcast("achievement.deleted", "achievement", {"id": achievement_id})
