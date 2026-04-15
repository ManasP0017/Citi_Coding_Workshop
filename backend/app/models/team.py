import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base


class Team(Base):
    __tablename__ = "teams"

    id                     = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name                   = Column(String(255), nullable=False)
    location               = Column(String(255), nullable=False, default="")
    organization_leader_id = Column(String(36), nullable=True)
    description            = Column(Text, nullable=False, default="")
    created_at             = Column(DateTime(timezone=True), nullable=False,
                                    default=lambda: datetime.now(timezone.utc))
    updated_at             = Column(DateTime(timezone=True), nullable=False,
                                    default=lambda: datetime.now(timezone.utc))

    members      = relationship("Member",      back_populates="team", lazy="dynamic",
                                cascade="save-update, merge")
    achievements = relationship("Achievement", back_populates="team", lazy="dynamic",
                                cascade="all, delete-orphan")
