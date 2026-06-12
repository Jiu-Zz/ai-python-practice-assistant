from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.entities import KnowledgePoint, Problem, TestCase, User


def seed_initial_data(db: Session) -> None:
    seed_users(db)
    seed_knowledge_points_and_problems(db)
    db.commit()


def seed_users(db: Session) -> None:
    if db.scalar(select(User).where(User.username == "student")) is None:
        db.add(
            User(
                username="student",
                email="student@example.com",
                nickname="演示学生",
                password_hash=hash_password("student123"),
                role="student",
                learning_stage="basic",
            )
        )
    if db.scalar(select(User).where(User.username == "admin")) is None:
        db.add(
            User(
                username="admin",
                email="admin@example.com",
                nickname="题库管理员",
                password_hash=hash_password("admin123"),
                role="admin",
                learning_stage="practice",
            )
        )


def seed_knowledge_points_and_problems(db: Session) -> None:
    if db.scalar(select(Problem).limit(1)) is not None:
        return

    kp_map = {}
    for name, category, description in [
        ("变量与输入输出", "基础语法", "读取输入、变量赋值、格式化输出"),
        ("条件判断", "基础语法", "if/elif/else 分支逻辑"),
        ("循环控制", "基础语法", "for、while 与循环边界"),
        ("列表", "数据结构", "列表遍历、索引与元素去重"),
        ("字符串", "数据结构", "字符串遍历、统计与格式处理"),
        ("函数", "代码组织", "函数参数、返回值与复用"),
        ("异常处理", "调试能力", "理解常见 Python 报错并定位问题"),
    ]:
        kp = KnowledgePoint(name=name, category=category, description=description)
        db.add(kp)
        kp_map[name] = kp

    problems = [
        Problem(
            title="判断奇偶",
            description="输入一个整数，输出它是 odd 还是 even。",
            difficulty="beginner",
            input_description="一行，一个整数 n。",
            output_description="若 n 为偶数输出 even，否则输出 odd。",
            sample_input="4\n",
            sample_output="even\n",
            starter_code="n = int(input())\n# 在这里补全判断逻辑\n",
            reference_solution="n = int(input())\nprint('even' if n % 2 == 0 else 'odd')\n",
            pass_rate=86,
            knowledge_points=[kp_map["变量与输入输出"], kp_map["条件判断"]],
            test_cases=[
                TestCase(input_data="4\n", expected_output="even\n", is_sample=True),
                TestCase(input_data="7\n", expected_output="odd\n"),
                TestCase(input_data="0\n", expected_output="even\n"),
            ],
        ),
        Problem(
            title="列表去重",
            description="输入一组整数，按原有顺序输出去重后的结果。",
            difficulty="basic",
            input_description="第一行是整数个数 n，第二行是 n 个整数。",
            output_description="输出去重后的整数，用空格分隔。",
            sample_input="6\n1 2 2 3 1 4\n",
            sample_output="1 2 3 4\n",
            starter_code=(
                "n = int(input())\n"
                "items = list(map(int, input().split()))\n"
                "result = []\n"
                "# 保持原顺序完成去重\n"
                "print(' '.join(map(str, result)))\n"
            ),
            reference_solution=(
                "n = int(input())\n"
                "items = list(map(int, input().split()))\n"
                "result = []\n"
                "for item in items:\n"
                "    if item not in result:\n"
                "        result.append(item)\n"
                "print(' '.join(map(str, result)))\n"
            ),
            pass_rate=61,
            knowledge_points=[kp_map["循环控制"], kp_map["列表"], kp_map["条件判断"]],
            test_cases=[
                TestCase(input_data="6\n1 2 2 3 1 4\n", expected_output="1 2 3 4\n", is_sample=True),
                TestCase(input_data="5\n5 5 5 5 5\n", expected_output="5\n"),
                TestCase(input_data="7\n3 1 3 2 1 4 2\n", expected_output="3 1 2 4\n"),
            ],
        ),
        Problem(
            title="统计字符串字符",
            description="输入一行字符串，统计其中英文字母、数字和其他字符的数量。",
            difficulty="intermediate",
            input_description="一行字符串。",
            output_description="依次输出 letters digits others 三个数量。",
            sample_input="Python3.9!\n",
            sample_output="6 2 2\n",
            starter_code=(
                "text = input()\n"
                "letters = digits = others = 0\n"
                "for ch in text:\n"
                "    pass\n"
                "print(letters, digits, others)\n"
            ),
            reference_solution=(
                "text = input()\n"
                "letters = digits = others = 0\n"
                "for ch in text:\n"
                "    if ch.isalpha():\n"
                "        letters += 1\n"
                "    elif ch.isdigit():\n"
                "        digits += 1\n"
                "    else:\n"
                "        others += 1\n"
                "print(letters, digits, others)\n"
            ),
            pass_rate=48,
            knowledge_points=[kp_map["字符串"], kp_map["循环控制"], kp_map["条件判断"]],
            test_cases=[
                TestCase(input_data="Python3.9!\n", expected_output="6 2 2\n", is_sample=True),
                TestCase(input_data="abc123\n", expected_output="3 3 0\n"),
                TestCase(input_data="Hi, AI 2026\n", expected_output="4 4 4\n"),
            ],
        ),
    ]
    db.add_all(problems)
