"""Member CRUD business logic."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.member import Member
from app.schemas.member import MemberCreate, MemberUpdate
from app.utils.serializers import model_to_dict


def create_member(req: MemberCreate, db: Session) -> dict:
    if db.query(Member).filter(Member.email == req.email.lower()).first():
        raise HTTPException(400, "Email already exists")
    data = req.model_dump()
    data["email"] = data["email"].lower()
    member = Member(id=str(uuid.uuid4()), **data)
    db.add(member)
    db.commit()
    db.refresh(member)
    return model_to_dict(member)


def list_members(db: Session, search: Optional[str] = None, team_id: Optional[str] = None) -> list[dict]:
    q = db.query(Member)
    if search:
        q = q.filter(Member.name.ilike(f"%{search}%") | Member.email.ilike(f"%{search}%"))
    if team_id:
        q = q.filter(Member.team_id == team_id)
    return [model_to_dict(m) for m in q.order_by(Member.name).all()]


def get_member(member_id: str, db: Session) -> dict:
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(404, "Member not found")
    return model_to_dict(member)


def update_member(member_id: str, req: MemberUpdate, db: Session) -> dict:
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(404, "Member not found")
    for field, value in req.model_dump(exclude_none=True).items():
        setattr(member, field, value)
    member.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(member)
    return model_to_dict(member)


def delete_member(member_id: str, db: Session) -> None:
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(404, "Member not found")
    db.delete(member)
    db.commit()
