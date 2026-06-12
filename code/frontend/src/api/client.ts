import type {
  AiTutorResponse,
  Dashboard,
  LearningPath,
  ProblemDetail,
  ProblemSummary,
  Recommendation,
  RunResult,
  SubmitResult,
  User
} from "../types";

type ApiEnvelope<T> = {
  success: boolean;
  data: T;
  message: string;
  trace_id: string;
};

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";
const TOKEN_KEY = "ai-python-practice-token";

const mockUser: User = {
  id: 1,
  username: "student",
  email: "student@example.com",
  nickname: "演示学生",
  role: "student",
  learning_stage: "basic"
};

const mockProblems: ProblemDetail[] = [
  {
    id: 1,
    title: "判断奇偶",
    difficulty: "beginner",
    status: "published",
    pass_rate: 86,
    knowledge_points: ["变量与输入输出", "条件判断"],
    completion_status: "not_started",
    description: "输入一个整数，输出它是 odd 还是 even。",
    input_description: "一行，一个整数 n。",
    output_description: "若 n 为偶数输出 even，否则输出 odd。",
    sample_input: "4\n",
    sample_output: "even\n",
    starter_code: "n = int(input())\n# 在这里补全判断逻辑\n"
  },
  {
    id: 2,
    title: "列表去重",
    difficulty: "basic",
    status: "published",
    pass_rate: 61,
    knowledge_points: ["循环控制", "列表", "条件判断"],
    completion_status: "wrong",
    description: "输入一组整数，按原有顺序输出去重后的结果。",
    input_description: "第一行是整数个数 n，第二行是 n 个整数。",
    output_description: "输出去重后的整数，用空格分隔。",
    sample_input: "6\n1 2 2 3 1 4\n",
    sample_output: "1 2 3 4\n",
    starter_code:
      "n = int(input())\nitems = list(map(int, input().split()))\nresult = []\n# 保持原顺序完成去重\nprint(' '.join(map(str, result)))\n"
  },
  {
    id: 3,
    title: "统计字符串字符",
    difficulty: "intermediate",
    status: "published",
    pass_rate: 48,
    knowledge_points: ["字符串", "循环控制", "条件判断"],
    completion_status: "not_started",
    description: "输入一行字符串，统计其中英文字母、数字和其他字符的数量。",
    input_description: "一行字符串。",
    output_description: "依次输出 letters digits others 三个数量。",
    sample_input: "Python3.9!\n",
    sample_output: "6 2 2\n",
    starter_code:
      "text = input()\nletters = digits = others = 0\nfor ch in text:\n    pass\nprint(letters, digits, others)\n"
  }
];

const mockDashboard: Dashboard = {
  completed_problem_count: 3,
  accepted_problem_count: 1,
  recent_pass_rate: 0.67,
  top_error_types: ["IndexError", "TypeError", "IndentationError"],
  weak_knowledge_points: ["列表", "函数", "循环控制"],
  trend: [
    { date: "2026-06-08", pass_rate: 0.4 },
    { date: "2026-06-09", pass_rate: 0.55 },
    { date: "2026-06-10", pass_rate: 0.72 }
  ]
};

async function request<T>(path: string, init: RequestInit = {}, fallback: T): Promise<T> {
  const token = localStorage.getItem(TOKEN_KEY);
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(init.headers ?? {})
      }
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const body = (await response.json()) as ApiEnvelope<T>;
    if (!body.success) {
      throw new Error(body.message);
    }
    return body.data;
  } catch {
    return fallback;
  }
}

export async function loginDemo(): Promise<User> {
  const fallback = { token: "mock-token", user: mockUser };
  const data = await request<{ token: string; user: User }>(
    "/api/v1/auth/login",
    {
      method: "POST",
      body: JSON.stringify({ account: "student", password: "student123" })
    },
    fallback
  );
  localStorage.setItem(TOKEN_KEY, data.token);
  return data.user;
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export function getDashboard() {
  return request<Dashboard>("/api/v1/dashboard/me", {}, mockDashboard);
}

export function getRecommendations() {
  const fallback: Recommendation[] = mockProblems.map((problem) => ({
    id: problem.id,
    title: problem.title,
    difficulty: problem.difficulty,
    pass_rate: problem.pass_rate,
    knowledge_points: problem.knowledge_points,
    reason: problem.id === 2 ? "针对薄弱点：列表" : "适合当前阶段继续练习"
  }));
  return request<Recommendation[]>("/api/v1/recommendations/today", {}, fallback);
}

export async function getProblems(): Promise<ProblemSummary[]> {
  const fallback = { items: mockProblems, total: mockProblems.length, page: 1, page_size: 20 };
  const data = await request<typeof fallback>("/api/v1/problems", {}, fallback);
  return data.items;
}

export function getProblem(problemId: number) {
  const fallback = mockProblems.find((item) => item.id === problemId) ?? mockProblems[0];
  return request<ProblemDetail>(`/api/v1/problems/${problemId}`, {}, fallback);
}

export function runCode(problemId: number, code: string, stdin: string) {
  const fallback: RunResult = {
    run_id: 0,
    status: "success",
    stdout: stdin ? "mock output\n" : "",
    stderr: "",
    time_ms: 42
  };
  return request<RunResult>(
    `/api/v1/problems/${problemId}/run`,
    { method: "POST", body: JSON.stringify({ code, stdin }) },
    fallback
  );
}

export function submitCode(problemId: number, code: string) {
  const fallback: SubmitResult = {
    submission_id: 0,
    status: "wrong_answer",
    passed_count: 1,
    total_count: 3,
    failed_cases: [
      {
        case_id: 2,
        input_preview: "5\\n5 5 5 5 5",
        expected_preview: "5",
        actual_preview: ""
      }
    ],
    error_type: undefined,
    score: 33,
    time_ms: 120
  };
  return request<SubmitResult>(
    `/api/v1/problems/${problemId}/submit`,
    { method: "POST", body: JSON.stringify({ code }) },
    fallback
  );
}

export function diagnose(problemId: number, code: string, stderr: string, submissionId?: number) {
  const fallback: AiTutorResponse = {
    record_id: 0,
    error_type: stderr ? "TypeError" : "WrongAnswer",
    summary: "代码可以运行或返回了错误信息，建议先从失败用例和输出格式开始定位。",
    possible_causes: ["输出格式与期望不一致", "循环中没有正确更新结果变量"],
    debug_steps: ["用样例手动跟踪变量变化", "对照失败用例检查实际输出"],
    related_concepts: ["列表", "循环控制"],
    hint_level: 1,
    hint_content: "先确认每个输入元素是否只处理一次，再检查最后的输出格式。",
    confidence: "medium"
  };
  return request<AiTutorResponse>(
    "/api/v1/ai/diagnose",
    {
      method: "POST",
      body: JSON.stringify({
        problem_id: problemId,
        submission_id: submissionId,
        code,
        stderr,
        failed_cases: [],
        request_type: "error_diagnosis"
      })
    },
    fallback
  );
}

export function getHint(problemId: number, code: string, hintLevel: number, lastSubmissionId?: number) {
  const fallback: AiTutorResponse = {
    record_id: 0,
    error_type: undefined,
    summary: "已按当前题目生成分层提示。",
    possible_causes: ["当前代码可能还缺少关键分支或结果更新逻辑"],
    debug_steps: ["运行样例并观察变量变化", "检查条件判断是否覆盖边界情况"],
    related_concepts: ["列表", "循环控制"],
    hint_level: hintLevel,
    hint_content:
      hintLevel === 1
        ? "先拆成输入、处理、输出三步。"
        : hintLevel === 2
          ? "重点看结果变量是否在循环中按条件更新。"
          : "可以在遍历时判断元素是否已经出现，再决定是否加入结果。",
    confidence: "medium"
  };
  return request<AiTutorResponse>(
    "/api/v1/ai/hints",
    {
      method: "POST",
      body: JSON.stringify({
        problem_id: problemId,
        code,
        hint_level: hintLevel,
        last_submission_id: lastSubmissionId
      })
    },
    fallback
  );
}

export function getLearningPath() {
  const fallback: LearningPath = {
    current_stage: "basic",
    summary: "根据最近提交记录生成学习路径；记录较少时优先推荐基础知识点。",
    recommended_topics: [
      { name: "列表", mastery: 0.36, status: "薄弱", reason: "最近提交通过率偏低，建议先补基础题。" },
      { name: "循环控制", mastery: 0.58, status: "巩固中", reason: "继续做同难度练习能稳定手感。" },
      { name: "条件判断", mastery: 0.78, status: "掌握较好", reason: "可以尝试综合题。" }
    ],
    recommended_problem_ids: [2, 3]
  };
  return request<LearningPath>("/api/v1/learning-path/me", {}, fallback);
}
