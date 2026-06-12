from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import api_response
from app.core.security import get_current_user
from app.models.entities import User
from app.schemas.ai import DiagnoseRequest, HintRequest
from app.services.ai_tutor_service import AiTutorService


router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/diagnose")
def diagnose(
    payload: DiagnoseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return api_response(AiTutorService(db).diagnose(current_user, payload))


@router.post("/hints")
def hints(
    payload: HintRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return api_response(AiTutorService(db).hint(current_user, payload))


@router.get("/records/{record_id}")
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return api_response(AiTutorService(db).get_record(current_user, record_id))
