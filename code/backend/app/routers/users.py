from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import api_response
from app.core.security import get_current_user
from app.models.entities import User
from app.schemas.user import ProfileUpdate
from app.services.auth_service import AuthService
from app.services.judge_service import JudgeService
from app.services.recommendation_service import RecommendationService


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return api_response(
        {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "nickname": current_user.nickname,
            "role": current_user.role,
            "learning_stage": current_user.learning_stage,
        }
    )


@router.put("/me/profile")
def update_profile(
    payload: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = AuthService(db).update_profile(current_user, payload)
    return api_response(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "nickname": user.nickname,
            "role": user.role,
            "learning_stage": user.learning_stage,
        }
    )


@router.get("/me/submissions")
def list_my_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return api_response(JudgeService(db).list_user_submissions(current_user))


@router.get("/me/weak-points")
def get_weak_points(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return api_response(RecommendationService(db).analyze_weak_points(current_user))
