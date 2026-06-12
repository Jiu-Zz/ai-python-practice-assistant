from typing import List, Optional

from pydantic import BaseModel


class RunCodeRequest(BaseModel):
    code: str
    stdin: str = ""


class RunCodeResponse(BaseModel):
    run_id: Optional[int] = None
    status: str
    stdout: str
    stderr: str
    time_ms: int
    memory_kb: Optional[int] = None
    error_type: Optional[str] = None


class SubmitCodeRequest(BaseModel):
    code: str


class FailedCase(BaseModel):
    case_id: int
    input_preview: str
    expected_preview: str
    actual_preview: str


class SubmitCodeResponse(BaseModel):
    submission_id: Optional[int] = None
    status: str
    passed_count: int
    total_count: int
    failed_cases: List[FailedCase]
    error_type: Optional[str] = None
    score: int = 0
    time_ms: int = 0


class SubmissionHistoryItem(BaseModel):
    id: int
    problem_id: int
    problem_title: str
    status: str
    score: int
    passed_count: int
    total_count: int
    error_type: Optional[str]
    created_at: str
