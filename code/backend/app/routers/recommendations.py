from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import api_response
from app.core.security import get_current_user
from app.models.entities import User
from app.services.recommendation_service import DashboardService, RecommendationService


router = APIRouter(tags=["recommendations"])


@router.get("/recommendations/today")
def today_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return api_response(RecommendationService(db).get_today_recommendations(current_user))


@router.get("/learning-path/me")
def learning_path(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return api_response(RecommendationService(db).get_learning_path(current_user))


@router.get("/dashboard/me")
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return api_response(DashboardService(db).get_dashboard(current_user))
