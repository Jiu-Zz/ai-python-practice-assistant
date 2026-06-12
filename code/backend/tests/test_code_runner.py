import unittest

from app.infrastructure.code_runner import CodeRunner, extract_error_type


class CodeRunnerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CodeRunner(output_limit=500)

    def test_run_success(self) -> None:
        result = self.runner.run("name = input()\nprint('hello', name)\n", "Python\n")

        self.assertEqual(result.status, "success")
        self.assertEqual(result.stdout.strip(), "hello Python")
        self.assertIsNone(result.error_type)

    def test_runtime_error_extracts_error_type(self) -> None:
        result = self.runner.run("print(1 / 0)\n")

        self.assertEqual(result.status, "runtime_error")
        self.assertEqual(result.error_type, "ZeroDivisionError")

    def test_blocks_unsafe_import(self) -> None:
        result = self.runner.run("import os\nprint(os.getcwd())\n")

        self.assertEqual(result.status, "runtime_error")
        self.assertEqual(result.error_type, "UnsafeCodeError")

    def test_timeout(self) -> None:
        result = self.runner.run("while True:\n    pass\n", timeout_seconds=1)

        self.assertEqual(result.status, "time_limit")
        self.assertEqual(result.error_type, "TimeoutError")

    def test_extract_error_type(self) -> None:
        stderr = "Traceback (most recent call last):\nTypeError: bad operand type\n"

        self.assertEqual(extract_error_type(stderr), "TypeError")


if __name__ == "__main__":
    unittest.main()
