"""Teams CRUD routes."""

from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_user, CanWrite, CanDelete
from app.core.broadcaster import broadcast
from app.schemas.team import TeamCreate, TeamUpdate
from app.schemas.common import MessageResponse, CreatedResponse
from app.services import team_service

router = APIRouter(prefix="/api/teams", tags=["teams"])


@router.post("", status_code=201)
async def create_team(
    req: TeamCreate,
    db: Session = Depends(get_db),
    _=Depends(CanWrite()),
):
    data = team_service.create_team(req, db)
    await broadcast("team.created", "team", data)
    return CreatedResponse(message="Team created successfully", id=data["id"])


@router.get("")
def get_teams(
    search: Optional[str] = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return {"teams": team_service.list_teams(db, search, location)}


@router.get("/{team_id}")
def get_team(
    team_id: str,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return team_service.get_team(team_id, db)


@router.put("/{team_id}")
async def update_team(
    team_id: str,
    req: TeamUpdate,
    db: Session = Depends(get_db),
    _=Depends(CanWrite()),
):
    data = team_service.update_team(team_id, req, db)
    await broadcast("team.updated", "team", data)
    return MessageResponse(message="Team updated successfully")


@router.delete("/{team_id}", status_code=204)
async def delete_team(
    team_id: str,
    db: Session = Depends(get_db),
    _=Depends(CanDelete()),
):
    team_service.delete_team(team_id, db)
    await broadcast("team.deleted", "team", {"id": team_id})
