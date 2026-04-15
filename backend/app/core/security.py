"""
Canonical security module.
Password hashing (bcrypt) and JWT creation / verification.
"""

from datetime import datetime, timezone, timedelta

import bcrypt
import jwt
from fastapi import HTTPException

from app.core.config import get_settings

settings = get_settings()


# ── Password helpers ──────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ── JWT helpers ───────────────────────────────────────────────────────────

def create_access_token(user_id: str, email: str, role: str) -> str:
    payload = {
        "user_id": user_id,
        "email":   email,
        "role":    role,
        "exp":     datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expiry_hours),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
