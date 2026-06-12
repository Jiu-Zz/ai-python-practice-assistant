import { Lightbulb, MessageSquare } from "lucide-react";
import type { AiTutorResponse } from "../types";

type AiPanelProps = {
  aiResponse: AiTutorResponse | null;
  hintLevel: number;
  onHintLevelChange: (level: number) => void;
  onDiagnose: () => void;
  onHint: () => void;
};

export function AiPanel({ aiResponse, hintLevel, onHintLevelChange, onDiagnose, onHint }: AiPanelProps) {
  return (
    <section className="workspace-panel ai-panel">
      <div className="section-heading">
        <MessageSquare size={18} />
        <h2>AI 助手</h2>
      </div>

      <div className="toolbar">
        <button className="command-button" type="button" onClick={onDiagnose}>
          <MessageSquare size={16} />
          诊断
        </button>
        <button className="command-button" type="button" onClick={onHint}>
          <Lightbulb size={16} />
          提示
        </button>
      </div>

      <div className="segmented">
        {[1, 2, 3].map((level) => (
          <button
            type="button"
            key={level}
            className={hintLevel === level ? "selected" : ""}
            onClick={() => onHintLevelChange(level)}
          >
            {level}
          </button>
        ))}
      </div>

      {aiResponse ? (
        <div className="ai-content">
          <strong>{aiResponse.error_type || "提示结果"}</strong>
          <p>{aiResponse.summary}</p>
          <div>
            <span className="field-label">建议步骤</span>
            <ol>
              {aiResponse.debug_steps.map((step) => (
                <li key={step}>{step}</li>
              ))}
            </ol>
          </div>
          <div className="hint-box">{aiResponse.hint_content}</div>
          <div className="tag-row">
            {aiResponse.related_concepts.map((concept) => (
              <span className="tag" key={concept}>
                {concept}
              </span>
            ))}
          </div>
        </div>
      ) : (
        <p className="muted">诊断和提示会显示在这里</p>
      )}
    </section>
  );
}
