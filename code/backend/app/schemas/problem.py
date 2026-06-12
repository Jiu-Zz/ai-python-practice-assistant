from typing import List, Optional

from pydantic import BaseModel, Field


class KnowledgePointRead(BaseModel):
    id: int
    name: str
    category: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class TestCaseCreate(BaseModel):
    input_data: str
    expected_output: str
    is_sample: bool = False
    weight: int = 1


class ProblemSummary(BaseModel):
    id: int
    title: str
    difficulty: str
    status: str
    pass_rate: int
    knowledge_points: List[str]
    completion_status: str = "not_started"


class ProblemDetail(ProblemSummary):
    description: str
    input_description: Optional[str] = None
    output_description: Optional[str] = None
    sample_input: Optional[str] = None
    sample_output: Optional[str] = None
    starter_code: Optional[str] = None


class ProblemCreate(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    description: str
    difficulty: str
    input_description: Optional[str] = None
    output_description: Optional[str] = None
    sample_input: Optional[str] = None
    sample_output: Optional[str] = None
    starter_code: Optional[str] = None
    reference_solution: Optional[str] = None
    status: str = "published"
    knowledge_points: List[str] = Field(default_factory=list)
    test_cases: List[TestCaseCreate] = Field(default_factory=list)


class ProblemUpdate(ProblemCreate):
    pass


class ProblemStatusUpdate(BaseModel):
    status: str
