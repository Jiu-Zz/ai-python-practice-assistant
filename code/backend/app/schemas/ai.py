from typing import List, Optional

from pydantic import BaseModel, Field


class FailedCasePreview(BaseModel):
    case_id: int
    input_preview: str
    expected_preview: str
    actual_preview: str


class DiagnoseRequest(BaseModel):
    problem_id: int
    submission_id: Optional[int] = None
    code: str
    stderr: Optional[str] = None
    failed_cases: List[FailedCasePreview] = Field(default_factory=list)
    request_type: str = "error_diagnosis"


class HintRequest(BaseModel):
    problem_id: int
    code: str
    hint_level: int = Field(ge=1, le=3)
    last_submission_id: Optional[int] = None


class AiTutorResponse(BaseModel):
    record_id: Optional[int] = None
    error_type: Optional[str] = None
    summary: str
    solution_code: Optional[str] = None
    possible_causes: List[str]
    debug_steps: List[str]
    related_concepts: List[str]
    hint_level: int
    hint_content: str
    confidence: str = "medium"
