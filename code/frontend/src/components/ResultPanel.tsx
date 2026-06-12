import { SquareTerminal } from "lucide-react";
import type { RunResult, SubmitResult } from "../types";
import { statusLabel } from "../utils/format";

type ResultPanelProps = {
  runResult: RunResult | null;
  submitResult: SubmitResult | null;
};

export function ResultPanel({ runResult, submitResult }: ResultPanelProps) {
  return (
    <section className="workspace-panel">
      <div className="section-heading">
        <SquareTerminal size={18} />
        <h2>运行反馈</h2>
      </div>
      {runResult ? (
        <div className="feedback-grid">
          <div>
            <span className="field-label">运行状态</span>
            <strong>{statusLabel(runResult.status)}</strong>
          </div>
          <div>
            <span className="field-label">耗时</span>
            <strong>{runResult.time_ms} ms</strong>
          </div>
        </div>
      ) : (
        <p className="muted">尚未运行</p>
      )}
      <pre className="output-box">{runResult?.stderr || runResult?.stdout || "输出会显示在这里"}</pre>

      <div className="section-heading compact">
        <h2>提交结果</h2>
      </div>
      {submitResult ? (
        <>
          <div className="feedback-grid">
            <div>
              <span className="field-label">通过情况</span>
              <strong>
                {submitResult.passed_count}/{submitResult.total_count}
              </strong>
            </div>
            <div>
              <span className="field-label">得分</span>
              <strong>{submitResult.score}</strong>
            </div>
          </div>
          {submitResult.failed_cases.length > 0 && (
            <div className="failed-list">
              {submitResult.failed_cases.map((item) => (
                <div className="failed-case" key={item.case_id}>
                  <b>Case {item.case_id}</b>
                  <span>输入：{item.input_preview || "-"}</span>
                  <span>期望：{item.expected_preview || "-"}</span>
                  <span>实际：{item.actual_preview || "-"}</span>
                </div>
              ))}
            </div>
          )}
        </>
      ) : (
        <p className="muted">尚未提交评测</p>
      )}
    </section>
  );
}
