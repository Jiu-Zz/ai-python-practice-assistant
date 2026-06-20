import { Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { getKnowledgePoints, getProblems } from "../api/client";
import { ProblemTable } from "../components/ProblemTable";
import type { ProblemSummary } from "../types";

type ProblemBankPageProps = {
  onPractice: (problemId: number) => void;
};

export function ProblemBankPage({ onPractice }: ProblemBankPageProps) {
  const [problems, setProblems] = useState<ProblemSummary[]>([]);
  const [knowledgePoints, setKnowledgePoints] = useState<string[]>([]);
  const [keyword, setKeyword] = useState("");
  const [difficulty, setDifficulty] = useState("all");
  const [knowledgePoint, setKnowledgePoint] = useState("all");
  const [status, setStatus] = useState("all");

  useEffect(() => {
    getProblems({ keyword, difficulty, knowledge_point: knowledgePoint, status }).then(setProblems);
  }, [difficulty, keyword, knowledgePoint, status]);

  useEffect(() => {
    getKnowledgePoints().then((items) => {
      setKnowledgePoints(Array.from(new Set(items.map((item) => item.name))));
    });
  }, []);

  return (
    <div className="page-stack">
      <section className="workspace-panel filter-row">
        <label className="search-box">
          <Search size={17} />
          <input value={keyword} onChange={(event) => setKeyword(event.target.value)} placeholder="搜索题目或知识点" />
        </label>
        <select value={difficulty} onChange={(event) => setDifficulty(event.target.value)}>
          <option value="all">全部难度</option>
          <option value="beginner">入门</option>
          <option value="basic">基础</option>
          <option value="intermediate">进阶</option>
        </select>
        <select value={knowledgePoint} onChange={(event) => setKnowledgePoint(event.target.value)}>
          <option value="all">全部知识点</option>
          {knowledgePoints.map((point) => (
            <option key={point} value={point}>
              {point}
            </option>
          ))}
        </select>
        <select value={status} onChange={(event) => setStatus(event.target.value)}>
          <option value="all">全部状态</option>
          <option value="not_started">未做</option>
          <option value="wrong">错题</option>
          <option value="accepted">已通过</option>
        </select>
      </section>
      <ProblemTable problems={problems} onPractice={onPractice} />
    </div>
  );
}
