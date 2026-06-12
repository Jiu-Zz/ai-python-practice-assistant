import { ArrowRight, CheckCircle2, CircleDashed, TriangleAlert } from "lucide-react";
import type { ProblemSummary } from "../types";
import { difficultyLabel } from "../utils/format";

type ProblemTableProps = {
  problems: ProblemSummary[];
  onPractice: (problemId: number) => void;
};

export function ProblemTable({ problems, onPractice }: ProblemTableProps) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>题目</th>
            <th>知识点</th>
            <th>难度</th>
            <th>通过率</th>
            <th>状态</th>
            <th aria-label="操作" />
          </tr>
        </thead>
        <tbody>
          {problems.map((problem) => (
            <tr key={problem.id}>
              <td>
                <strong>{problem.title}</strong>
              </td>
              <td>
                <div className="tag-row">
                  {problem.knowledge_points.map((point) => (
                    <span className="tag" key={point}>
                      {point}
                    </span>
                  ))}
                </div>
              </td>
              <td>{difficultyLabel(problem.difficulty)}</td>
              <td>{problem.pass_rate}%</td>
              <td>
                <span className={`status ${problem.completion_status}`}>
                  {statusIcon(problem.completion_status)}
                  {statusLabel(problem.completion_status)}
                </span>
              </td>
              <td>
                <button className="icon-button" type="button" onClick={() => onPractice(problem.id)} title="开始练习">
                  <ArrowRight size={17} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function statusLabel(status: string) {
  if (status === "accepted") return "已通过";
  if (status === "wrong") return "错题";
  return "未做";
}

function statusIcon(status: string) {
  if (status === "accepted") return <CheckCircle2 size={15} />;
  if (status === "wrong") return <TriangleAlert size={15} />;
  return <CircleDashed size={15} />;
}
