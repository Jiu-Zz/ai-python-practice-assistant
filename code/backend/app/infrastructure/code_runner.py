import ast
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from typing import Optional

from app.core.config import settings


@dataclass
class RunResult:
    status: str
    stdout: str
    stderr: str
    error_type: Optional[str]
    time_ms: int
    memory_kb: Optional[int] = None


class UnsafeCodeError(ValueError):
    pass


class CodeRunner:
    banned_modules = {
        "os",
        "subprocess",
        "socket",
        "shutil",
        "pathlib",
        "multiprocessing",
        "threading",
    }
    banned_calls = {
        "open",
        "exec",
        "eval",
        "compile",
        "__import__",
        "breakpoint",
    }
    banned_attributes = {
        "system",
        "popen",
        "remove",
        "unlink",
        "rmdir",
        "rmtree",
    }

    def __init__(self, output_limit: int = settings.code_output_limit) -> None:
        self.output_limit = output_limit

    def run(self, code: str, stdin: str = "", timeout_seconds: int = settings.code_run_timeout_seconds) -> RunResult:
        started = time.perf_counter()
        try:
            self._validate(code)
        except UnsafeCodeError as exc:
            return RunResult(
                status="runtime_error",
                stdout="",
                stderr=str(exc),
                error_type="UnsafeCodeError",
                time_ms=self._elapsed_ms(started),
            )

        with tempfile.TemporaryDirectory(prefix="py-practice-") as temp_dir:
            source_path = os.path.join(temp_dir, "main.py")
            with open(source_path, "w", encoding="utf-8") as source_file:
                source_file.write(code)

            try:
                completed = subprocess.run(
                    [sys.executable, "-I", source_path],
                    input=stdin,
                    text=True,
                    capture_output=True,
                    timeout=timeout_seconds,
                    cwd=temp_dir,
                )
            except subprocess.TimeoutExpired as exc:
                stdout = self._limit(exc.stdout or "")
                stderr = self._limit(exc.stderr or "代码运行超时，请检查是否存在死循环。")
                return RunResult(
                    status="time_limit",
                    stdout=stdout,
                    stderr=stderr,
                    error_type="TimeoutError",
                    time_ms=self._elapsed_ms(started),
                )

        stdout = self._limit(completed.stdout)
        stderr = self._limit(completed.stderr)
        error_type = extract_error_type(stderr)
        status = "success" if completed.returncode == 0 else "runtime_error"
        return RunResult(
            status=status,
            stdout=stdout,
            stderr=stderr,
            error_type=error_type,
            time_ms=self._elapsed_ms(started),
        )

    def _validate(self, code: str) -> None:
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_name = alias.name.split(".", 1)[0]
                    if root_name in self.banned_modules:
                        raise UnsafeCodeError(f"当前练习环境暂不允许导入模块：{root_name}")
            elif isinstance(node, ast.ImportFrom):
                root_name = (node.module or "").split(".", 1)[0]
                if root_name in self.banned_modules:
                    raise UnsafeCodeError(f"当前练习环境暂不允许导入模块：{root_name}")
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in self.banned_calls:
                    raise UnsafeCodeError(f"当前练习环境暂不允许调用：{node.func.id}()")
                if isinstance(node.func, ast.Attribute) and node.func.attr in self.banned_attributes:
                    raise UnsafeCodeError(f"当前练习环境暂不允许调用：{node.func.attr}()")

    def _limit(self, value: str) -> str:
        if len(value) <= self.output_limit:
            return value
        return value[: self.output_limit] + "\n...输出过长，已截断..."

    @staticmethod
    def _elapsed_ms(started: float) -> int:
        return int((time.perf_counter() - started) * 1000)


def extract_error_type(stderr: str) -> Optional[str]:
    if not stderr:
        return None
    matches = re.findall(r"^([A-Za-z_][A-Za-z0-9_]*(?:Error|Exception)):", stderr, flags=re.MULTILINE)
    if matches:
        return matches[-1]
    if "SyntaxError" in stderr:
        return "SyntaxError"
    if "IndentationError" in stderr:
        return "IndentationError"
    return None
