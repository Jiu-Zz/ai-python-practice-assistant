from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.models.entities import KnowledgePoint, Problem, Submission, TestCase, User
from app.repositories.problem_repository import ProblemRepository
from app.schemas.problem import ProblemCreate, ProblemStatusUpdate, ProblemUpdate


class ProblemService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.problems = ProblemRepository(db)

    def list_problems(
        self,
        current_user: Optional[User],
        keyword: Optional[str],
        knowledge_point: Optional[str],
        difficulty: Optional[str],
        status: Optional[str],
        page: int,
        page_size: int,
    ) -> dict:
        items, total = self.problems.list_published(keyword, knowledge_point, difficulty, page, page_size)
        summaries = [self._summary(problem, current_user) for problem in items]
        if status:
            summaries = [item for item in summaries if item["completion_status"] == status]
        return {"items": summaries, "total": total, "page": page, "page_size": page_size}

    def get_problem_detail(self, problem_id: int, current_user: Optional[User]) -> dict:
        problem = self.problems.get_published(problem_id)
        if problem is None:
            raise NotFoundError("题目不存在或已下架")
        detail = self._summary(problem, current_user)
        detail.update(
            {
                "description": problem.description,
                "input_description": problem.input_description,
                "output_description": problem.output_description,
                "sample_input": problem.sample_input,
                "sample_output": problem.sample_output,
                "starter_code": problem.starter_code,
            }
        )
        return detail

    def create_problem(self, payload: ProblemCreate) -> dict:
        problem = Problem(
            title=payload.title,
            description=payload.description,
            difficulty=payload.difficulty,
            input_description=payload.input_description,
            output_description=payload.output_description,
            sample_input=payload.sample_input,
            sample_output=payload.sample_output,
            starter_code=payload.starter_code,
            reference_solution=payload.reference_solution,
            status=payload.status,
        )
        for name in payload.knowledge_points:
            problem.knowledge_points.append(self.problems.find_or_create_knowledge_point(name))
        for item in payload.test_cases:
            problem.test_cases.append(
                TestCase(
                    input_data=item.input_data,
                    expected_output=item.expected_output,
                    is_sample=item.is_sample,
                    weight=item.weight,
                )
            )
        self.db.add(problem)
        self.db.commit()
        self.db.refresh(problem)
        return self._summary(problem, None)

    def update_problem(self, problem_id: int, payload: ProblemUpdate) -> dict:
        problem = self.problems.get_any(problem_id)
        if problem is None:
            raise NotFoundError("题目不存在")
        for field in [
            "title",
            "description",
            "difficulty",
            "input_description",
            "output_description",
            "sample_input",
            "sample_output",
            "starter_code",
            "reference_solution",
            "status",
        ]:
            setattr(problem, field, getattr(payload, field))
        problem.knowledge_points = [
            self.problems.find_or_create_knowledge_point(name) for name in payload.knowledge_points
        ]
        problem.test_cases = [
            TestCase(
                input_data=item.input_data,
                expected_output=item.expected_output,
                is_sample=item.is_sample,
                weight=item.weight,
            )
            for item in payload.test_cases
        ]
        self.db.add(problem)
        self.db.commit()
        self.db.refresh(problem)
        return self._summary(problem, None)

    def update_status(self, problem_id: int, payload: ProblemStatusUpdate) -> dict:
        problem = self.problems.get_any(problem_id)
        if problem is None:
            raise NotFoundError("题目不存在")
        problem.status = payload.status
        self.db.add(problem)
        self.db.commit()
        self.db.refresh(problem)
        return self._summary(problem, None)

    def _summary(self, problem: Problem, current_user: Optional[User]) -> dict:
        completion_status = "not_started"
        if current_user is not None:
            latest = self.db.scalar(
                select(Submission)
                .where(Submission.problem_id == problem.id, Submission.user_id == current_user.id)
                .order_by(Submission.created_at.desc())
            )
            if latest is not None:
                completion_status = "accepted" if latest.status == "accepted" else "wrong"
        return {
            "id": problem.id,
            "title": problem.title,
            "difficulty": problem.difficulty,
            "status": problem.status,
            "pass_rate": problem.pass_rate,
            "knowledge_points": [kp.name for kp in problem.knowledge_points],
            "completion_status": completion_status,
        }

    def list_knowledge_points(self) -> list:
        points = self.db.scalars(select(KnowledgePoint).order_by(KnowledgePoint.category, KnowledgePoint.name)).all()
        return [
            {
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "description": item.description,
            }
            for item in points
        ]
