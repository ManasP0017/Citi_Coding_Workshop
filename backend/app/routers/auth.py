"""Auth routes — register, login, me."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, MeResponse
from app.schemas.common import CreatedResponse
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=CreatedResponse, status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    result = auth_service.register_user(req, db)
    return CreatedResponse(message=result["message"], id=result["user_id"])


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    token = auth_service.login_user(req.email, req.password, db)
    return TokenResponse(token=token)


@router.get("/me", response_model=MeResponse)
def me(current_user: User = Depends(get_current_user)):
    return MeResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
    )
