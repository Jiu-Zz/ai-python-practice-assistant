from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import api_response
from app.core.security import get_current_user, get_optional_current_user, require_admin
from app.models.entities import User
from app.schemas.judge import RunCodeRequest, SubmitCodeRequest
from app.schemas.problem import ProblemCreate, ProblemStatusUpdate, ProblemUpdate
from app.services.judge_service import JudgeService
from app.services.problem_service import ProblemService


router = APIRouter(tags=["problems"])


@router.get("/knowledge-points")
def list_knowledge_points(db: Session = Depends(get_db)):
    return api_response(ProblemService(db).list_knowledge_points())


@router.get("/problems")
def list_problems(
    keyword: Optional[str] = None,
    knowledge_point: Optional[str] = None,
    difficulty: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    data = ProblemService(db).list_problems(
        current_user=current_user,
        keyword=keyword,
        knowledge_point=knowledge_point,
        difficulty=difficulty,
        status=status,
        page=page,
        page_size=page_size,
    )
    return api_response(data)


@router.get("/problems/{problem_id}")
def get_problem(
    problem_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    return api_response(ProblemService(db).get_problem_detail(problem_id, current_user))


@router.post("/problems/{problem_id}/run")
def run_code(
    problem_id: int,
    payload: RunCodeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return api_response(JudgeService(db).run_code(problem_id, current_user, payload))


@router.post("/problems/{problem_id}/submit")
def submit_code(
    problem_id: int,
    payload: SubmitCodeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return api_response(JudgeService(db).submit_code(problem_id, current_user, payload))


@router.get("/submissions/{submission_id}")
def get_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return api_response(JudgeService(db).get_submission(submission_id, current_user))


@router.post("/admin/problems")
def create_problem(
    payload: ProblemCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return api_response(ProblemService(db).create_problem(payload))


@router.put("/admin/problems/{problem_id}")
def update_problem(
    problem_id: int,
    payload: ProblemUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return api_response(ProblemService(db).update_problem(problem_id, payload))


@router.patch("/admin/problems/{problem_id}/status")
def update_problem_status(
    problem_id: int,
    payload: ProblemStatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return api_response(ProblemService(db).update_status(problem_id, payload))
