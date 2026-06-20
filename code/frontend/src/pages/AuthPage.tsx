import { GraduationCap, LogIn, UserPlus } from "lucide-react";
import { useState } from "react";
import type { User } from "../types";

type AuthMode = "login" | "register";

type AuthPageProps = {
  onLogin: (account: string, password: string) => Promise<void>;
  onRegister: (payload: {
    username: string;
    email: string;
    password: string;
    learning_stage: string;
    nickname?: string;
  }) => Promise<void>;
  loading: boolean;
  error: string | null;
  demoUser?: User | null;
};

export function AuthPage({ onLogin, onRegister, loading, error, demoUser }: AuthPageProps) {
  const [mode, setMode] = useState<AuthMode>("login");
  const [loginForm, setLoginForm] = useState({ account: "student", password: "student123" });
  const [registerForm, setRegisterForm] = useState({
    username: "",
    email: "",
    nickname: "",
    password: "",
    learning_stage: "basic"
  });

  async function handleSubmit() {
    if (mode === "login") {
      await onLogin(loginForm.account.trim(), loginForm.password);
      return;
    }
    await onRegister({
      username: registerForm.username.trim(),
      email: registerForm.email.trim(),
      nickname: registerForm.nickname.trim() || undefined,
      password: registerForm.password,
      learning_stage: registerForm.learning_stage
    });
  }

  return (
    <div className="auth-shell">
      <section className="auth-panel auth-hero">
        <div className="brand large">
          <GraduationCap size={32} />
          <span>PyCoach</span>
        </div>
        <h1>AI 驱动的 Python 编程练习助手</h1>
        <p>
          先登录，再开始完整体验题目推荐、在线编程、运行评测、错误诊断和学习路径推荐。
        </p>
        <div className="auth-highlights">
          <div className="auth-highlight">
            <strong>练习闭环</strong>
            <span>选题、编码、运行、提交、诊断一屏完成。</span>
          </div>
          <div className="auth-highlight">
            <strong>分层提示</strong>
            <span>按思路、定位、关键建议逐级辅助，而不是直接给答案。</span>
          </div>
          <div className="auth-highlight">
            <strong>成长反馈</strong>
            <span>根据提交记录和错误类型生成薄弱点与下一步建议。</span>
          </div>
        </div>
        <div className="demo-box">
          <span className="field-label">演示账号</span>
          <strong>{demoUser?.username ?? "student"} / student123</strong>
        </div>
      </section>

      <section className="auth-panel auth-form-panel">
        <div className="segmented auth-mode-switch">
          <button type="button" className={mode === "login" ? "selected" : ""} onClick={() => setMode("login")}>
            登录
          </button>
          <button
            type="button"
            className={mode === "register" ? "selected" : ""}
            onClick={() => setMode("register")}
          >
            注册
          </button>
        </div>

        <div className="auth-form">
          {mode === "login" ? (
            <>
              <label>
                <span className="field-label">账号或邮箱</span>
                <input
                  value={loginForm.account}
                  onChange={(event) => setLoginForm((prev) => ({ ...prev, account: event.target.value }))}
                  placeholder="student"
                />
              </label>
              <label>
                <span className="field-label">密码</span>
                <input
                  type="password"
                  value={loginForm.password}
                  onChange={(event) => setLoginForm((prev) => ({ ...prev, password: event.target.value }))}
                  placeholder="请输入密码"
                />
              </label>
            </>
          ) : (
            <>
              <label>
                <span className="field-label">用户名</span>
                <input
                  value={registerForm.username}
                  onChange={(event) => setRegisterForm((prev) => ({ ...prev, username: event.target.value }))}
                  placeholder="至少 3 个字符"
                />
              </label>
              <label>
                <span className="field-label">邮箱</span>
                <input
                  type="email"
                  value={registerForm.email}
                  onChange={(event) => setRegisterForm((prev) => ({ ...prev, email: event.target.value }))}
                  placeholder="name@example.com"
                />
              </label>
              <label>
                <span className="field-label">昵称</span>
                <input
                  value={registerForm.nickname}
                  onChange={(event) => setRegisterForm((prev) => ({ ...prev, nickname: event.target.value }))}
                  placeholder="可选"
                />
              </label>
              <label>
                <span className="field-label">学习阶段</span>
                <select
                  value={registerForm.learning_stage}
                  onChange={(event) => setRegisterForm((prev) => ({ ...prev, learning_stage: event.target.value }))}
                >
                  <option value="zero">零基础</option>
                  <option value="basic">基础语法</option>
                  <option value="practice">刷题巩固</option>
                </select>
              </label>
              <label>
                <span className="field-label">密码</span>
                <input
                  type="password"
                  value={registerForm.password}
                  onChange={(event) => setRegisterForm((prev) => ({ ...prev, password: event.target.value }))}
                  placeholder="至少 6 位"
                />
              </label>
            </>
          )}
        </div>

        {error ? <div className="error-banner">{error}</div> : null}

        <button className="primary-button auth-submit" type="button" onClick={handleSubmit} disabled={loading}>
          {mode === "login" ? <LogIn size={16} /> : <UserPlus size={16} />}
          {loading ? "处理中..." : mode === "login" ? "进入练习系统" : "注册并进入"}
        </button>
      </section>
    </div>
  );
}
