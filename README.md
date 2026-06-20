# AI 驱动的 Python 编程练习助手

## 项目简介

本项目是一个面向 Python 初学者的交互式 Web 学习应用，计划集成 AI 助手能力，为用户提供个性化编程练习、错误诊断和学习路径推荐。

项目的核心目标不是简单提供题库或聊天问答，而是围绕“练习 - 诊断 - 提示 - 成长反馈”构建完整学习闭环，帮助初学者在编写 Python 代码、理解报错和规划后续学习时获得更及时、更可解释的支持。

## 核心功能规划

- 题目推荐：根据学习阶段、历史表现和薄弱知识点推荐 Python 练习。
- 在线编程：提供题目详情、代码编辑和运行入口。
- 运行/提交反馈：展示运行输出、测试用例通过情况和失败原因。
- AI 错误诊断：解释常见 Python 报错，给出可能原因和排查建议。
- 分层提示：按思路提示、定位提示、关键代码建议逐级引导，避免直接给答案。
- 学习路径：基于练习记录和错误画像推荐下一阶段学习内容。

## 当前阶段

当前仓库已完成需求分析、功能草图与概要设计阶段，已完成：

- 业务场景与用户核心诉求分析
- 功能边界与首期 MVP 范围定义
- 核心业务流程梳理
- 低保真功能草图与页面结构规划
- 系统整体架构、模块接口、核心数据结构与关键业务逻辑设计

## 文档入口

- [需求分析说明书](docs/需求分析说明书.md)
- [功能草图](docs/功能草图.md)
- [概要设计说明书](docs/概要设计说明书.md)

## 当前工程结构

```text
.
├── code/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── core/
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   ├── routers/
│   │   │   ├── services/
│   │   │   ├── repositories/
│   │   │   ├── infrastructure/
│   │   │   └── data/
│   │   ├── tests/
│   │   └── requirements.txt
│   └── frontend/
│       ├── src/
│       │   ├── api/
│       │   ├── components/
│       │   ├── pages/
│       │   ├── store/
│       │   └── utils/
│       └── package.json
├── README.md
├── docs/
│   ├── 需求分析说明书.md
│   ├── 功能草图.md
│   └── 概要设计说明书.md
└── .gitignore
```

## 本地启动

### Docker Compose

如果本机已安装 Docker，可在项目根目录一条命令启动前后端：

```bash
docker compose up --build
```

启动后访问：

- 前端：`http://127.0.0.1:5173`
- 后端：`http://127.0.0.1:8000`
- 接口文档：`http://127.0.0.1:8000/docs`

停止服务：

```bash
docker compose down
```

如需清空演示数据库：

```bash
docker compose down -v
```

### 后端

```bash
cd code/backend
python3.11 -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS / Linux
# source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

后端默认地址为 `http://127.0.0.1:8000`，接口文档为 `http://127.0.0.1:8000/docs`。

说明：后端依赖要求 Python `3.11+`。如果系统默认 `python` 不是 3.11，Windows 下可使用 `py -3.11` 创建虚拟环境。

启动时会自动创建 SQLite 数据库并写入演示账号：

- 学生账号：`student` / `student123`
- 管理员账号：`admin` / `admin123`

### 前端

```bash
cd code/frontend
npm install
npm run dev
```

前端默认地址为 `http://127.0.0.1:5173`。开发期如果后端未启动，页面会使用 mock 数据渲染，方便先调整界面。

若 `5173` 端口已被占用，Vite 会自动切换到下一个可用端口，例如 `5174`。

## 后续计划

1. 完善认证体验和题库管理页面。
2. 接入真实 LLM Provider，并保留本地模板兜底。
3. 增加提交历史、错题本和学习路径的前后端联动细节。
4. 编写测试设计及结果报告，覆盖核心功能、异常输入和用户体验流程。
5. 完成项目总结 PPT 与最终提交材料整理。
