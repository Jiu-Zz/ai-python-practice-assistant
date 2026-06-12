export type PageKey = "dashboard" | "problems" | "practice" | "path" | "profile";

export type User = {
  id: number;
  username: string;
  email: string;
  nickname?: string;
  role: string;
  learning_stage: string;
};

export type ProblemSummary = {
  id: number;
  title: string;
  difficulty: "beginner" | "basic" | "intermediate" | string;
  status: string;
  pass_rate: number;
  knowledge_points: string[];
  completion_status: "not_started" | "accepted" | "wrong" | string;
};

export type ProblemDetail = ProblemSummary & {
  description: string;
  input_description?: string;
  output_description?: string;
  sample_input?: string;
  sample_output?: string;
  starter_code?: string;
};

export type Dashboard = {
  completed_problem_count: number;
  accepted_problem_count: number;
  recent_pass_rate: number;
  top_error_types: string[];
  weak_knowledge_points: string[];
  trend: Array<{ date: string; pass_rate: number }>;
};

export type Recommendation = {
  id: number;
  title: string;
  difficulty: string;
  pass_rate: number;
  knowledge_points: string[];
  reason: string;
};

export type RunResult = {
  run_id?: number;
  status: string;
  stdout: string;
  stderr: string;
  time_ms: number;
  memory_kb?: number;
  error_type?: string;
};

export type SubmitResult = {
  submission_id?: number;
  status: string;
  passed_count: number;
  total_count: number;
  failed_cases: Array<{
    case_id: number;
    input_preview: string;
    expected_preview: string;
    actual_preview: string;
  }>;
  error_type?: string;
  score: number;
  time_ms: number;
};

export type AiTutorResponse = {
  record_id?: number;
  error_type?: string;
  summary: string;
  possible_causes: string[];
  debug_steps: string[];
  related_concepts: string[];
  hint_level: number;
  hint_content: string;
  confidence: string;
};

export type LearningPath = {
  current_stage: string;
  summary: string;
  recommended_topics: Array<{
    name: string;
    mastery: number;
    status: string;
    reason: string;
  }>;
  recommended_problem_ids: number[];
};
