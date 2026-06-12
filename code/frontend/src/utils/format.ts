export function difficultyLabel(value: string) {
  const labels: Record<string, string> = {
    beginner: "入门",
    basic: "基础",
    intermediate: "进阶"
  };
  return labels[value] ?? value;
}

export function statusLabel(value: string) {
  const labels: Record<string, string> = {
    success: "运行成功",
    runtime_error: "运行错误",
    time_limit: "运行超时",
    accepted: "已通过",
    wrong_answer: "答案错误"
  };
  return labels[value] ?? value;
}
