import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Member(Base):
    __tablename__ = "members"

    id              = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name            = Column(String(255), nullable=False)
    email           = Column(String(255), unique=True, nullable=False, index=True)
    team_id         = Column(String(36), ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    role            = Column(String(100), nullable=False, default="member")
    is_team_leader  = Column(Boolean, nullable=False, default=False)
    is_direct_staff = Column(Boolean, nullable=False, default=True)
    location        = Column(String(255), nullable=False, default="")
    created_at      = Column(DateTime(timezone=True), nullable=False,
                             default=lambda: datetime.now(timezone.utc))
    updated_at      = Column(DateTime(timezone=True), nullable=False,
                             default=lambda: datetime.now(timezone.utc))

    team = relationship("Team", back_populates="members")
