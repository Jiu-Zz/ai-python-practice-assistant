from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.infrastructure.code_runner import CodeRunner
from app.models.entities import Problem, RunRecord, Submission, TestResult, User
from app.repositories.problem_repository import ProblemRepository
from app.schemas.judge import RunCodeRequest, SubmitCodeRequest


class JudgeService:
    def __init__(self, db: Session, runner: CodeRunner = None) -> None:
        self.db = db
        self.runner = runner or CodeRunner()
        self.problems = ProblemRepository(db)

    def run_code(self, problem_id: int, current_user: User, payload: RunCodeRequest) -> dict:
        problem = self.problems.get_published(problem_id)
        if problem is None:
            raise NotFoundError("题目不存在或已下架")

        result = self.runner.run(payload.code, payload.stdin)
        record = RunRecord(
            user_id=current_user.id,
            problem_id=problem_id,
            code=payload.code,
            stdin=payload.stdin,
            stdout=result.stdout,
            stderr=result.stderr,
            status=result.status,
            error_type=result.error_type,
            time_ms=result.time_ms,
            memory_kb=result.memory_kb,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return {
            "run_id": record.id,
            "status": result.status,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "time_ms": result.time_ms,
            "memory_kb": result.memory_kb,
            "error_type": result.error_type,
        }

    def submit_code(self, problem_id: int, current_user: User, payload: SubmitCodeRequest) -> dict:
        problem = self.problems.get_published(problem_id)
        if problem is None:
            raise NotFoundError("题目不存在或已下架")

        test_cases = self.problems.get_test_cases(problem_id, include_hidden=True)
        if not test_cases:
            raise NotFoundError("题目暂未配置测试用例")

        submission = Submission(
            user_id=current_user.id,
            problem_id=problem_id,
            code=payload.code,
            status="wrong_answer",
            total_count=len(test_cases),
        )
        self.db.add(submission)
        self.db.flush()

        passed_count = 0
        failed_cases = []
        overall_status = "accepted"
        first_error_type = None
        total_time_ms = 0

        for case in test_cases:
            result = self.runner.run(payload.code, case.input_data)
            total_time_ms += result.time_ms
            case_status = self._case_status(result.status, result.stdout, case.expected_output)
            if case_status == "passed":
                passed_count += 1
            else:
                if overall_status == "accepted":
                    overall_status = result.status if result.status != "success" else "wrong_answer"
                if first_error_type is None:
                    first_error_type = result.error_type
                if len(failed_cases) < 3:
                    failed_cases.append(
                        {
                            "case_id": case.id,
                            "input_preview": self._preview(case.input_data),
                            "expected_preview": self._preview(case.expected_output),
                            "actual_preview": self._preview(result.stderr or result.stdout),
                        }
                    )

            self.db.add(
                TestResult(
                    submission_id=submission.id,
                    test_case_id=case.id,
                    status=case_status,
                    actual_output=result.stdout,
                    error_message=result.stderr,
                    time_ms=result.time_ms,
                )
            )

        score = int(passed_count / len(test_cases) * 100)
        submission.status = overall_status
        submission.passed_count = passed_count
        submission.error_type = first_error_type
        submission.score = score
        submission.time_ms = total_time_ms
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)

        return {
            "submission_id": submission.id,
            "status": submission.status,
            "passed_count": passed_count,
            "total_count": len(test_cases),
            "failed_cases": failed_cases,
            "error_type": first_error_type,
            "score": score,
            "time_ms": total_time_ms,
        }

    def get_submission(self, submission_id: int, current_user: User) -> dict:
        submission = self.db.get(Submission, submission_id)
        if submission is None or submission.user_id != current_user.id:
            raise NotFoundError("提交记录不存在")
        return self._submission_item(submission)

    def list_user_submissions(self, current_user: User) -> List[dict]:
        submissions = self.db.scalars(
            select(Submission)
            .where(Submission.user_id == current_user.id)
            .order_by(Submission.created_at.desc())
            .limit(50)
        ).all()
        return [self._submission_item(item) for item in submissions]

    @staticmethod
    def _case_status(status: str, stdout: str, expected_output: str) -> str:
        if status == "time_limit":
            return "time_limit"
        if status != "success":
            return "runtime_error"
        return "passed" if stdout.strip() == expected_output.strip() else "failed"

    @staticmethod
    def _preview(value: str, limit: int = 120) -> str:
        compact = value.strip().replace("\n", "\\n")
        if len(compact) <= limit:
            return compact
        return compact[:limit] + "..."

    @staticmethod
    def _submission_item(submission: Submission) -> dict:
        problem_title = submission.problem.title if isinstance(submission.problem, Problem) else ""
        return {
            "id": submission.id,
            "problem_id": submission.problem_id,
            "problem_title": problem_title,
            "status": submission.status,
            "score": submission.score,
            "passed_count": submission.passed_count,
            "total_count": submission.total_count,
            "error_type": submission.error_type,
            "created_at": submission.created_at.isoformat(),
        }
