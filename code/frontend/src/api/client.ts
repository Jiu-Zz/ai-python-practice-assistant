import type {
  AiTutorResponse,
  AuthPayload,
  Dashboard,
  LearningPath,
  ProblemDetail,
  ProblemSummary,
  Recommendation,
  RunResult,
  SubmissionHistoryItem,
  SubmitResult,
  User
} from "../types";

type ApiEnvelope<T> = {
  success: boolean;
  data: T;
  message: string;
  trace_id: string;
};

const API_BASE = String(import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000")
  .trim()
  .replace(/\/+$/, "");
const TOKEN_KEY = "ai-python-practice-token";
const MEMORY_TOKEN_KEY = "__ai_python_practice_token__";

export class ApiError extends Error {
  status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function getApiUrl(path: string) {
  return `${API_BASE}${path}`;
}

function getStorage() {
  try {
    return window.localStorage;
  } catch {
    return null;
  }
}

function getMemoryToken() {
  return (globalThis as Record<string, unknown>)[MEMORY_TOKEN_KEY] as string | undefined;
}

function setMemoryToken(token: string | null) {
  const bag = globalThis as Record<string, unknown>;
  if (token === null) {
    delete bag[MEMORY_TOKEN_KEY];
    return;
  }
  bag[MEMORY_TOKEN_KEY] = token;
}

function getToken() {
  const storage = getStorage();
  if (storage) {
    try {
      const token = storage.getItem(TOKEN_KEY);
      if (token) return token;
    } catch {
      // ignore storage access issues and fall back to memory
    }
  }
  return getMemoryToken() ?? null;
}

function setToken(token: string) {
  const storage = getStorage();
  if (storage) {
    try {
      storage.setItem(TOKEN_KEY, token);
    } catch {
      // ignore storage access issues and keep an in-memory session instead
    }
  }
  setMemoryToken(token);
}

export function clearToken() {
  const storage = getStorage();
  if (storage) {
    try {
      storage.removeItem(TOKEN_KEY);
    } catch {
      // ignore storage access issues
    }
  }
  setMemoryToken(null);
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getToken();
  const response = await fetch(getApiUrl(path), {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init.headers ?? {})
    }
  });

  let body: ApiEnvelope<T> | null = null;
  try {
    body = (await response.json()) as ApiEnvelope<T>;
  } catch {
    if (!response.ok) {
      throw new ApiError(`请求失败 (${response.status})`, response.status);
    }
    throw new ApiError("接口返回了无法解析的响应", response.status);
  }

  if (!response.ok || !body.success) {
    const message = body?.message || `请求失败 (${response.status})`;
    if (response.status === 401) {
      clearToken();
    }
    throw new ApiError(message, response.status);
  }

  return body.data;
}

export async function login(account: string, password: string): Promise<User> {
  const data = await request<AuthPayload>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({ account, password })
  });
  setToken(data.token);
  return data.user;
}

export async function register(payload: {
  username: string;
  email: string;
  password: string;
  learning_stage: string;
  nickname?: string;
}): Promise<User> {
  const data = await request<AuthPayload>("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify(payload)
  });
  setToken(data.token);
  return data.user;
}

export function getCurrentUser() {
  return request<User>("/api/v1/users/me");
}

export function updateProfile(payload: { nickname?: string; learning_stage?: string }) {
  return request<User>("/api/v1/users/me/profile", {
    method: "PUT",
    body: JSON.stringify(payload)
  });
}

export function getDashboard() {
  return request<Dashboard>("/api/v1/dashboard/me");
}

export function getRecommendations() {
  return request<Recommendation[]>("/api/v1/recommendations/today");
}

export function getKnowledgePoints() {
  return request<Array<{ id: number; name: string; category: string; description?: string }>>(
    "/api/v1/knowledge-points"
  );
}

export async function getProblems(filters?: {
  keyword?: string;
  difficulty?: string;
  knowledge_point?: string;
  status?: string;
}) {
  const params = new URLSearchParams();
  if (filters?.keyword) params.set("keyword", filters.keyword);
  if (filters?.difficulty && filters.difficulty !== "all") params.set("difficulty", filters.difficulty);
  if (filters?.knowledge_point && filters.knowledge_point !== "all") params.set("knowledge_point", filters.knowledge_point);
  if (filters?.status && filters.status !== "all") params.set("status", filters.status);

  const query = params.toString();
  const data = await request<{ items: ProblemSummary[]; total: number; page: number; page_size: number }>(
    `/api/v1/problems${query ? `?${query}` : ""}`
  );
  return data.items;
}

export function getProblem(problemId: number) {
  return request<ProblemDetail>(`/api/v1/problems/${problemId}`);
}

export function runCode(problemId: number, code: string, stdin: string) {
  return request<RunResult>(`/api/v1/problems/${problemId}/run`, {
    method: "POST",
    body: JSON.stringify({ code, stdin })
  });
}

export function submitCode(problemId: number, code: string) {
  return request<SubmitResult>(`/api/v1/problems/${problemId}/submit`, {
    method: "POST",
    body: JSON.stringify({ code })
  });
}

export function diagnose(
  problemId: number,
  code: string,
  stderr: string,
  failedCases: SubmitResult["failed_cases"],
  submissionId?: number
) {
  return request<AiTutorResponse>("/api/v1/ai/diagnose", {
    method: "POST",
    body: JSON.stringify({
      problem_id: problemId,
      submission_id: submissionId,
      code,
      stderr,
      failed_cases: failedCases,
      request_type: "error_diagnosis"
    })
  });
}

export function getHint(problemId: number, code: string, hintLevel: number, lastSubmissionId?: number) {
  return request<AiTutorResponse>("/api/v1/ai/hints", {
    method: "POST",
    body: JSON.stringify({
      problem_id: problemId,
      code,
      hint_level: hintLevel,
      last_submission_id: lastSubmissionId
    })
  });
}

export function getLearningPath() {
  return request<LearningPath>("/api/v1/learning-path/me");
}

export function getSubmissionHistory() {
  return request<SubmissionHistoryItem[]>("/api/v1/users/me/submissions");
}

export function hasStoredSession() {
  return Boolean(getToken());
}
