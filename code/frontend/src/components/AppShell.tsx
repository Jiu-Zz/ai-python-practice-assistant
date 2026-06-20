import { BookOpen, Code2, GraduationCap, LayoutDashboard, LogOut, TrendingUp, UserRound } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";
import type { PageKey, User } from "../types";

type NavItem = {
  key: PageKey;
  label: string;
  icon: LucideIcon;
};

const navItems: NavItem[] = [
  { key: "dashboard", label: "首页", icon: LayoutDashboard },
  { key: "problems", label: "练习题库", icon: BookOpen },
  { key: "practice", label: "在线练习", icon: Code2 },
  { key: "path", label: "学习路径", icon: TrendingUp },
  { key: "profile", label: "个人中心", icon: UserRound }
];

type AppShellProps = {
  currentPage: PageKey;
  onPageChange: (page: PageKey) => void;
  user: User | null;
  onLogout: () => void;
  children: ReactNode;
};

export function AppShell({ currentPage, onPageChange, user, onLogout, children }: AppShellProps) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <GraduationCap size={24} />
          <span>PyCoach</span>
        </div>
        <nav className="nav-list">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.key}
                className={item.key === currentPage ? "nav-item active" : "nav-item"}
                onClick={() => onPageChange(item.key)}
                type="button"
                title={item.label}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>
      <main className="main-area">
        <header className="topbar">
          <div>
            <p className="eyebrow">AI Python Practice Assistant</p>
            <h1>{pageTitle(currentPage)}</h1>
          </div>
          <div className="topbar-actions">
            <div className="user-chip">
              <UserRound size={17} />
              <span>{user?.nickname || user?.username || "演示学生"}</span>
            </div>
            <button className="icon-button" type="button" title="退出登录" onClick={onLogout}>
              <LogOut size={17} />
            </button>
          </div>
        </header>
        {children}
      </main>
    </div>
  );
}

function pageTitle(page: PageKey) {
  const titles: Record<PageKey, string> = {
    dashboard: "学习仪表盘",
    problems: "练习题库",
    practice: "题目练习页",
    path: "学习路径",
    profile: "个人中心"
  };
  return titles[page];
}
