import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Achievement(Base):
    __tablename__ = "achievements"

    id          = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title       = Column(String(255), nullable=False)
    description = Column(Text, nullable=False, default="")
    team_id     = Column(String(36), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    month       = Column(String(20), nullable=False)
    year        = Column(Integer, nullable=False)
    created_at  = Column(DateTime(timezone=True), nullable=False,
                         default=lambda: datetime.now(timezone.utc))
    updated_at  = Column(DateTime(timezone=True), nullable=False,
                         default=lambda: datetime.now(timezone.utc))

    team = relationship("Team", back_populates="achievements")
