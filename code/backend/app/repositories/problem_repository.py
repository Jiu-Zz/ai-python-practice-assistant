from typing import List, Optional, Tuple

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.entities import KnowledgePoint, Problem, TestCase


class ProblemRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_published(
        self,
        keyword: Optional[str] = None,
        knowledge_point: Optional[str] = None,
        difficulty: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Problem], int]:
        query = select(Problem).where(Problem.status == "published")
        if keyword:
            like = f"%{keyword}%"
            query = query.where(or_(Problem.title.like(like), Problem.description.like(like)))
        if difficulty:
            query = query.where(Problem.difficulty == difficulty)
        if knowledge_point:
            query = query.join(Problem.knowledge_points).where(KnowledgePoint.name == knowledge_point)

        all_items = list(self.db.scalars(query.order_by(Problem.id.asc())).unique())
        start = max(page - 1, 0) * page_size
        end = start + page_size
        return all_items[start:end], len(all_items)

    def get_published(self, problem_id: int) -> Optional[Problem]:
        return self.db.scalar(
            select(Problem).where(Problem.id == problem_id, Problem.status == "published")
        )

    def get_any(self, problem_id: int) -> Optional[Problem]:
        return self.db.get(Problem, problem_id)

    def get_test_cases(self, problem_id: int, include_hidden: bool = False) -> List[TestCase]:
        query = select(TestCase).where(TestCase.problem_id == problem_id).order_by(TestCase.id.asc())
        if not include_hidden:
            query = query.where(TestCase.is_sample.is_(True))
        return list(self.db.scalars(query))

    def find_or_create_knowledge_point(self, name: str, category: str = "基础语法") -> KnowledgePoint:
        knowledge_point = self.db.scalar(select(KnowledgePoint).where(KnowledgePoint.name == name))
        if knowledge_point is not None:
            return knowledge_point
        knowledge_point = KnowledgePoint(name=name, category=category, description=f"{name} 相关基础知识")
        self.db.add(knowledge_point)
        self.db.flush()
        return knowledge_point
