import { Play, SendHorizontal } from "lucide-react";
import { useEffect, useState } from "react";
import { diagnose, getHint, getProblem, runCode, submitCode } from "../api/client";
import { AiPanel } from "../components/AiPanel";
import { CodeEditor } from "../components/CodeEditor";
import { ResultPanel } from "../components/ResultPanel";
import type { AiTutorResponse, ProblemDetail, RunResult, SubmitResult } from "../types";
import { difficultyLabel } from "../utils/format";

type PracticePageProps = {
  problemId: number;
};

export function PracticePage({ problemId }: PracticePageProps) {
  const [problem, setProblem] = useState<ProblemDetail | null>(null);
  const [code, setCode] = useState("");
  const [stdin, setStdin] = useState("");
  const [runResult, setRunResult] = useState<RunResult | null>(null);
  const [submitResult, setSubmitResult] = useState<SubmitResult | null>(null);
  const [aiResponse, setAiResponse] = useState<AiTutorResponse | null>(null);
  const [hintLevel, setHintLevel] = useState(1);

  useEffect(() => {
    getProblem(problemId).then((next) => {
      setProblem(next);
      setCode(next.starter_code ?? "");
      setStdin(next.sample_input ?? "");
      setRunResult(null);
      setSubmitResult(null);
      setAiResponse(null);
    });
  }, [problemId]);

  async function handleRun() {
    const result = await runCode(problemId, code, stdin);
    setRunResult(result);
  }

  async function handleSubmit() {
    const result = await submitCode(problemId, code);
    setSubmitResult(result);
  }

  async function handleDiagnose() {
    const response = await diagnose(
      problemId,
      code,
      runResult?.stderr ?? "",
      submitResult?.submission_id
    );
    setAiResponse(response);
  }

  async function handleHint() {
    const response = await getHint(problemId, code, hintLevel, submitResult?.submission_id);
    setAiResponse(response);
  }

  return (
    <div className="practice-layout">
      <section className="workspace-panel problem-detail">
        <div className="problem-title-row">
          <div>
            <p className="eyebrow">题目</p>
            <h2>{problem?.title ?? "加载中"}</h2>
          </div>
          {problem && <span className="difficulty-pill">{difficultyLabel(problem.difficulty)}</span>}
        </div>
        <p>{problem?.description}</p>
        <div className="tag-row">
          {problem?.knowledge_points.map((point) => (
            <span className="tag" key={point}>
              {point}
            </span>
          ))}
        </div>
        <dl className="spec-list">
          <div>
            <dt>输入</dt>
            <dd>{problem?.input_description}</dd>
          </div>
          <div>
            <dt>输出</dt>
            <dd>{problem?.output_description}</dd>
          </div>
          <div>
            <dt>样例</dt>
            <dd>
              <code>{problem?.sample_input?.trim()}</code>
              <span>→</span>
              <code>{problem?.sample_output?.trim()}</code>
            </dd>
          </div>
        </dl>
      </section>

      <AiPanel
        aiResponse={aiResponse}
        hintLevel={hintLevel}
        onHintLevelChange={setHintLevel}
        onDiagnose={handleDiagnose}
        onHint={handleHint}
      />

      <section className="workspace-panel code-workbench">
        <CodeEditor value={code} onChange={setCode} />
        <div className="runner-bar">
          <label>
            <span>标准输入</span>
            <textarea value={stdin} onChange={(event) => setStdin(event.target.value)} rows={2} />
          </label>
          <div className="runner-actions">
            <button className="command-button" type="button" onClick={handleRun}>
              <Play size={16} />
              运行
            </button>
            <button className="primary-button" type="button" onClick={handleSubmit}>
              <SendHorizontal size={16} />
              提交
            </button>
          </div>
        </div>
      </section>

      <ResultPanel runResult={runResult} submitResult={submitResult} />
    </div>
  );
}
