"""Authentication business logic."""

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.core.rbac import VALID_ROLES
from app.models.user import User
from app.schemas.auth import RegisterRequest


def register_user(req: RegisterRequest, db: Session) -> dict:
    if db.query(User).filter(User.email == req.email.lower()).first():
        raise HTTPException(400, "Email already registered")
    user = User(
        id=str(uuid.uuid4()),
        email=req.email.lower(),
        password=hash_password(req.password),
        name=req.name.strip(),
        role=req.role,
    )
    db.add(user)
    db.commit()
    return {"message": "User registered successfully", "user_id": user.id}


def login_user(email: str, password: str, db: Session) -> str:
    user = db.query(User).filter(User.email == email.strip().lower()).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(401, "Invalid email or password")
    return create_access_token(user.id, user.email, user.role)
