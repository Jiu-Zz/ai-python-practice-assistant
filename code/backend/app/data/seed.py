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
        kp = db.scalar(select(KnowledgePoint).where(KnowledgePoint.name == name))
        if kp is None:
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
            title="成绩分级",
            description="输入一个 0 到 100 之间的分数，输出对应等级 A、B、C、D 或 E。",
            difficulty="beginner",
            input_description="一行，一个整数 score。",
            output_description="90 及以上输出 A，80-89 输出 B，70-79 输出 C，60-69 输出 D，其余输出 E。",
            sample_input="85\n",
            sample_output="B\n",
            starter_code="score = int(input())\n# 在这里补全分支逻辑\n",
            reference_solution=(
                "score = int(input())\n"
                "if score >= 90:\n"
                "    print('A')\n"
                "elif score >= 80:\n"
                "    print('B')\n"
                "elif score >= 70:\n"
                "    print('C')\n"
                "elif score >= 60:\n"
                "    print('D')\n"
                "else:\n"
                "    print('E')\n"
            ),
            pass_rate=82,
            knowledge_points=[kp_map["变量与输入输出"], kp_map["条件判断"]],
            test_cases=[
                TestCase(input_data="85\n", expected_output="B\n", is_sample=True),
                TestCase(input_data="92\n", expected_output="A\n"),
                TestCase(input_data="58\n", expected_output="E\n"),
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
            title="打印乘法表",
            description="输入一个整数 n，按行输出从 1 到 n 的乘法表。",
            difficulty="basic",
            input_description="一行，一个整数 n。",
            output_description="第 i 行输出从 1*i 到 i*i 的等式，等式之间用一个空格分隔。",
            sample_input="3\n",
            sample_output="1*1=1\n1*2=2 2*2=4\n1*3=3 2*3=6 3*3=9\n",
            starter_code="n = int(input())\n# 使用循环构造每一行并输出\n",
            reference_solution=(
                "n = int(input())\n"
                "for i in range(1, n + 1):\n"
                "    row = []\n"
                "    for j in range(1, i + 1):\n"
                "        row.append(f'{j}*{i}={i * j}')\n"
                "    print(' '.join(row))\n"
            ),
            pass_rate=64,
            knowledge_points=[kp_map["循环控制"], kp_map["字符串"]],
            test_cases=[
                TestCase(
                    input_data="3\n",
                    expected_output="1*1=1\n1*2=2 2*2=4\n1*3=3 2*3=6 3*3=9\n",
                    is_sample=True,
                ),
                TestCase(input_data="1\n", expected_output="1*1=1\n"),
                TestCase(input_data="2\n", expected_output="1*1=1\n1*2=2 2*2=4\n"),
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
        Problem(
            title="单词计数",
            description="输入一行由空格分隔的单词，输出每个单词出现的次数，按首次出现顺序展示。",
            difficulty="intermediate",
            input_description="一行字符串，单词之间使用单个空格分隔。",
            output_description="每行输出 word:count。",
            sample_input="apple banana apple\n",
            sample_output="apple:2\nbanana:1\n",
            starter_code="words = input().split()\n# 统计并保持首次出现顺序\n",
            reference_solution=(
                "words = input().split()\n"
                "counts = {}\n"
                "order = []\n"
                "for word in words:\n"
                "    if word not in counts:\n"
                "        counts[word] = 0\n"
                "        order.append(word)\n"
                "    counts[word] += 1\n"
                "for word in order:\n"
                "    print(f'{word}:{counts[word]}')\n"
            ),
            pass_rate=46,
            knowledge_points=[kp_map["字符串"], kp_map["列表"], kp_map["循环控制"]],
            test_cases=[
                TestCase(input_data="apple banana apple\n", expected_output="apple:2\nbanana:1\n", is_sample=True),
                TestCase(input_data="hi hi hi\n", expected_output="hi:3\n"),
                TestCase(input_data="one two three\n", expected_output="one:1\ntwo:1\nthree:1\n"),
            ],
        ),
        Problem(
            title="函数求平均值",
            description="输入一组整数，定义函数计算它们的平均值并保留两位小数输出。",
            difficulty="basic",
            input_description="第一行是整数个数 n，第二行是 n 个整数。",
            output_description="输出平均值，保留两位小数。",
            sample_input="4\n1 2 3 4\n",
            sample_output="2.50\n",
            starter_code=(
                "def calc_avg(nums):\n"
                "    # 返回平均值\n"
                "    pass\n\n"
                "n = int(input())\n"
                "nums = list(map(int, input().split()))\n"
                "print(f'{calc_avg(nums):.2f}')\n"
            ),
            reference_solution=(
                "def calc_avg(nums):\n"
                "    return sum(nums) / len(nums)\n\n"
                "n = int(input())\n"
                "nums = list(map(int, input().split()))\n"
                "print(f'{calc_avg(nums):.2f}')\n"
            ),
            pass_rate=58,
            knowledge_points=[kp_map["函数"], kp_map["变量与输入输出"]],
            test_cases=[
                TestCase(input_data="4\n1 2 3 4\n", expected_output="2.50\n", is_sample=True),
                TestCase(input_data="3\n3 3 3\n", expected_output="3.00\n"),
                TestCase(input_data="5\n2 4 6 8 10\n", expected_output="6.00\n"),
            ],
        ),
    ]
    existing_titles = set(db.scalars(select(Problem.title)).all())
    for problem in problems:
        if problem.title not in existing_titles:
            db.add(problem)
