import json
from typing import Optional

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.infrastructure.code_runner import extract_error_type
from app.infrastructure.llm_client import LlmClient
from app.models.entities import AiRecord, Problem, Submission, User
from app.repositories.problem_repository import ProblemRepository
from app.schemas.ai import DiagnoseRequest, HintRequest


class AiTutorService:
    def __init__(self, db: Session, llm_client: Optional[LlmClient] = None) -> None:
        self.db = db
        self.llm_client = llm_client or LlmClient()
        self.problems = ProblemRepository(db)

    def diagnose(self, current_user: User, payload: DiagnoseRequest) -> dict:
        problem = self.problems.get_published(payload.problem_id)
        if problem is None:
            raise NotFoundError("题目不存在或已下架")

        error_type = extract_error_type(payload.stderr or "") or "WrongAnswer"
        response = self._diagnosis_template(error_type, problem, payload)
        record = self._save_record(
            current_user=current_user,
            problem=problem,
            submission_id=payload.submission_id,
            request_type="diagnosis",
            prompt_summary=f"{problem.title}:{error_type}",
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

        response = self._hint_template(problem, payload.hint_level)
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
    def _diagnosis_template(error_type: str, problem: Problem, payload: DiagnoseRequest) -> dict:
        concepts = [kp.name for kp in problem.knowledge_points] or ["Python 基础语法"]
        templates = {
            "SyntaxError": (
                "代码存在语法错误，Python 在解析代码时还没开始运行就停下来了。",
                ["检查括号、冒号、引号是否成对", "确认 if/for/while/def 行末是否缺少冒号"],
                ["先看 Traceback 最后一行附近的行号", "从报错行向上一两行检查结构是否闭合"],
            ),
            "IndentationError": (
                "代码缩进不符合 Python 的代码块规则。",
                ["同一代码块内混用了不同缩进层级", "if、for、while 或函数体下一行没有正确缩进"],
                ["定位提示中的行号", "确认同一层代码左侧空格数量一致"],
            ),
            "TypeError": (
                "某个运算或函数调用拿到了不合适的数据类型。",
                ["把字符串和整数直接拼接", "对列表、None 或数字使用了不匹配的操作"],
                ["在报错行前用 type() 临时查看变量类型", "确认输入读取后是否需要 int() 或 str() 转换"],
            ),
            "IndexError": (
                "代码访问了列表或字符串中不存在的位置。",
                ["循环范围比列表长度多了一位", "没有处理空列表或边界元素"],
                ["检查 range 的结束值", "确认访问前索引小于 len(...)"],
            ),
            "WrongAnswer": (
                "代码可以运行，但输出和测试用例期望结果不一致。",
                ["没有覆盖重复值、空输入或边界值", "输出格式多了空格、少了换行或顺序不对"],
                ["先用样例手算一遍", "对照失败用例检查每一步中间结果"],
            ),
        }
        summary, causes, steps = templates.get(error_type, templates["WrongAnswer"])
        return {
            "record_id": None,
            "error_type": error_type,
            "summary": summary,
            "possible_causes": causes,
            "debug_steps": steps,
            "related_concepts": concepts,
            "hint_level": 1,
            "hint_content": "先不要急着改整段代码，建议从 Traceback 或失败用例指出的位置开始，验证输入、变量类型和输出格式。",
            "confidence": "medium",
        }

    @staticmethod
    def _hint_template(problem: Problem, hint_level: int) -> dict:
        concepts = [kp.name for kp in problem.knowledge_points] or ["Python 基础语法"]
        if hint_level == 1:
            content = f"先把题目拆成输入、处理、输出三步。本题重点关注：{', '.join(concepts)}。"
        elif hint_level == 2:
            content = "重点检查循环边界、条件判断和结果变量的更新位置，确保每个输入元素只按题意处理一次。"
        else:
            content = "可以写一个结果列表或计数变量，在遍历时按条件更新；最后统一格式化输出，避免在循环中提前输出最终答案。"
        return {
            "record_id": None,
            "error_type": None,
            "summary": "已按当前题目生成分层提示。",
            "possible_causes": ["当前代码可能还缺少关键分支或结果更新逻辑"],
            "debug_steps": ["用样例输入手动跟踪变量变化", "运行一次后对照实际输出和期望输出"],
            "related_concepts": concepts,
            "hint_level": hint_level,
            "hint_content": content,
            "confidence": "medium",
        }
