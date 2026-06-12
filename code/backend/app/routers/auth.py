from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import api_response
from app.schemas.user import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    return api_response(AuthService(db).register(payload))


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return api_response(AuthService(db).login(payload))
