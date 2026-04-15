"""Insights analytics routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_user
from app.schemas.insights import InsightsResponse
from app.services import insights_service

router = APIRouter(prefix="/api/insights", tags=["insights"])


@router.get("", response_model=InsightsResponse)
def get_insights(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return insights_service.get_insights(db)
