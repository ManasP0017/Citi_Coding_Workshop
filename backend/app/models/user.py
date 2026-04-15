import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id         = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email      = Column(String(255), unique=True, nullable=False, index=True)
    password   = Column(String(255), nullable=False)
    name       = Column(String(255), nullable=False)
    role       = Column(String(50), nullable=False, default="viewer")
    created_at = Column(DateTime(timezone=True), nullable=False,
                        default=lambda: datetime.now(timezone.utc))
