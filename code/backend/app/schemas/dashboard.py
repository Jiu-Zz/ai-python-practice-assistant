from typing import List

from pydantic import BaseModel


class TrendItem(BaseModel):
    date: str
    pass_rate: float


class DashboardResponse(BaseModel):
    completed_problem_count: int
    accepted_problem_count: int
    recent_pass_rate: float
    top_error_types: List[str]
    weak_knowledge_points: List[str]
    trend: List[TrendItem]
    ai_request_count: int = 0


class LearningTopic(BaseModel):
    name: str
    mastery: float
    status: str
    reason: str


class LearningPathResponse(BaseModel):
    current_stage: str
    summary: str
    recommended_topics: List[LearningTopic]
    recommended_problem_ids: List[int]
