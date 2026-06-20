import json
from typing import Optional

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.models.entities import AiRecord, Problem, Submission, User
from app.repositories.problem_repository import ProblemRepository
from app.schemas.ai import DiagnoseRequest, HintRequest


class AiTutorService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.problems = ProblemRepository(db)

    def diagnose(self, current_user: User, payload: DiagnoseRequest) -> dict:
        problem = self.problems.get_published(payload.problem_id)
        if problem is None:
            raise NotFoundError("题目不存在或已下架")

        response = self._diagnose_template(problem.title)
        response["record_id"] = None
        record = self._save_record(
            current_user=current_user,
            problem=problem,
            submission_id=payload.submission_id,
            request_type="diagnosis",
            prompt_summary=f"{problem.title}:code_review",
            response=response,
            hint_level=response["hint_level"],
            confidence=response["confidence"],
        )
        response["record_id"] = record.id
        return response

    def hint(self, current_user: User, payload: HintRequest) -> dict:
        problem = self.problems.get_published(payload.problem_id)
        if problem is None:
            raise NotFoundError("题目不存在或已下架")

        response = self._hint_template(problem.title, payload.hint_level)
        response["record_id"] = None
        record = self._save_record(
            current_user=current_user,
            problem=problem,
            submission_id=payload.last_submission_id,
            request_type="hint",
            prompt_summary=f"{problem.title}:hint:{payload.hint_level}",
            response=response,
            hint_level=payload.hint_level,
            confidence=response["confidence"],
        )
        response["record_id"] = record.id
        return response

    def get_record(self, current_user: User, record_id: int) -> dict:
        record = self.db.get(AiRecord, record_id)
        if record is None or record.user_id != current_user.id:
            raise NotFoundError("AI 记录不存在")
        data = json.loads(record.response_json)
        data["record_id"] = record.id
        return data

    def _save_record(
        self,
        current_user: User,
        problem: Problem,
        submission_id: Optional[int],
        request_type: str,
        prompt_summary: str,
        response: dict,
        hint_level: Optional[int],
        confidence: str,
    ) -> AiRecord:
        if submission_id is not None:
            submission = self.db.get(Submission, submission_id)
            if submission is None or submission.user_id != current_user.id:
                submission_id = None
        record = AiRecord(
            user_id=current_user.id,
            problem_id=problem.id,
            submission_id=submission_id,
            request_type=request_type,
            prompt_summary=prompt_summary,
            response_json=json.dumps(response, ensure_ascii=False),
            hint_level=hint_level,
            confidence=confidence,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    @staticmethod
    def _diagnose_template(problem_title: str) -> dict:
        if problem_title == "判断奇偶":
            return {
                "error_type": "题目讲解",
                "summary": "需求理解：接收一个整数，判断奇偶。能被 2 整除是偶数 (even)，不能则是奇数 (odd)。",
                "solution_code": "n = int(input())\nif n % 2 == 0:\n    print(\"even\")\nelse:\n    print(\"odd\")",
                "possible_causes": [
                    "核心判断逻辑：整数对 2 取余，n % 2 == 0 -> 偶数，n % 2 != 0 -> 奇数",
                    "代码分步思路：读取键盘输入，转为整数 n = int(input())",
                ],
                "debug_steps": [
                    "第一步：读取键盘输入，转为整数 n = int(input())",
                    "第二步：用 if 条件判断取余结果",
                    "第三步：按规则输出对应字符串",
                ],
                "related_concepts": ["输入输出", "取模运算", "条件判断"],
                "hint_level": 1,
                "hint_content": (
                    "第一步：读取键盘输入，转为整数 n = int(input())\n"
                    "第二步：用 if 条件判断取余结果\n"
                    "第三步：按规则输出对应字符串"
                ),
                "confidence": "high",
            }

        return {
            "error_type": "题目讲解",
            "summary": f"这道题目《{problem_title}》可以按输入、处理、输出三步来拆开看。",
            "solution_code": None,
            "possible_causes": [
                "先把题目拆成输入、处理、输出三步",
                "把样例代入代码，检查每一步是否符合题意",
            ],
            "debug_steps": [
                "逐行看代码，确认每个变量的作用和更新时机",
                "把样例输入代入，检查中间状态是否符合题意",
            ],
            "related_concepts": ["输入输出", "条件判断", "循环控制", "函数"],
            "hint_level": 1,
            "hint_content": "先把代码拆成输入、处理、输出三块，逐段核对是否和题意一致。",
            "confidence": "medium",
        }

    @staticmethod
    def _hint_template(problem_title: str, hint_level: int) -> dict:
        if problem_title == "判断奇偶":
            content_map = {
                1: "需求理解：接收一个整数，判断奇偶。",
                2: "核心判断逻辑：整数对 2 取余，n % 2 == 0 -> 偶数，n % 2 != 0 -> 奇数。",
                3: "代码分步思路：第一步读入并转成整数；第二步判断取余结果；第三步输出对应字符串。",
            }
            level = max(1, min(3, hint_level))
            return {
                "error_type": "题目讲解",
                "summary": "这道题的标准写法很短，重点是输入、判断、输出三步。",
                "solution_code": "n = int(input())\nif n % 2 == 0:\n    print(\"even\")\nelse:\n    print(\"odd\")",
                "possible_causes": [
                    "输入必须先转成整数",
                    "偶数和奇数可以通过 `% 2` 区分",
                ],
                "debug_steps": [
                    "第一步：读取键盘输入，转为整数 n = int(input())",
                    "第二步：用 if 条件判断取余结果",
                    "第三步：按规则输出对应字符串",
                ],
                "related_concepts": ["输入输出", "取模运算", "条件判断"],
                "hint_level": level,
                "hint_content": content_map[level],
                "confidence": "high",
            }

        level = max(1, min(3, hint_level))
        return {
            "error_type": "题目讲解",
            "summary": f"这道题目《{problem_title}》先把题意拆开，再逐步实现。",
            "solution_code": None,
            "possible_causes": [
                "先把题目拆成输入、处理、输出三步",
                "把样例代入代码，检查每一步是否符合题意",
            ],
            "debug_steps": [
                "逐行看代码，确认每个变量的作用和更新时机",
                "把样例输入代入，检查中间状态是否符合题意",
            ],
            "related_concepts": ["输入输出", "条件判断", "循环控制", "函数"],
            "hint_level": level,
            "hint_content": "先把代码拆成输入、处理、输出三块，逐段核对是否和题意一致。",
            "confidence": "medium",
        }
