"""Members CRUD routes."""

from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_user, CanWrite, CanDelete
from app.core.broadcaster import broadcast
from app.schemas.member import MemberCreate, MemberUpdate
from app.schemas.common import MessageResponse, CreatedResponse
from app.services import member_service

router = APIRouter(prefix="/api/members", tags=["members"])


@router.post("", status_code=201)
async def create_member(
    req: MemberCreate,
    db: Session = Depends(get_db),
    _=Depends(CanWrite()),
):
    data = member_service.create_member(req, db)
    await broadcast("member.created", "member", data)
    return CreatedResponse(message="Member created successfully", id=data["id"])


@router.get("")
def get_members(
    search: Optional[str] = None,
    team_id: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return {"members": member_service.list_members(db, search, team_id)}


@router.get("/{member_id}")
def get_member(
    member_id: str,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return member_service.get_member(member_id, db)


@router.put("/{member_id}")
async def update_member(
    member_id: str,
    req: MemberUpdate,
    db: Session = Depends(get_db),
    _=Depends(CanWrite()),
):
    data = member_service.update_member(member_id, req, db)
    await broadcast("member.updated", "member", data)
    return MessageResponse(message="Member updated successfully")


@router.delete("/{member_id}", status_code=204)
async def delete_member(
    member_id: str,
    db: Session = Depends(get_db),
    _=Depends(CanDelete()),
):
    member_service.delete_member(member_id, db)
    await broadcast("member.deleted", "member", {"id": member_id})
