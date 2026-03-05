# CodingEngine 项目上下文

## 项目定位

CodingEngine 以 simplerig 为编排骨架，融合 ECC/OMO 的 Agent 定义、Skill 模式和反馈机制，构建「编排+执行+迭代」解决方案。目标：将 SWE-bench ~50% 模型推到 70-80%+。

## 三大能力

1. **编排能力** — 按 context_limit 拆分任务，DAG 依赖，并行执行
2. **执行能力** — 原子提交、解耦、可回滚
3. **迭代能力** — verify 失败 → 诊断 → 重试（最多 3 轮）

## 目录结构

```
CursorCodingEngine/
├── .cursor/
│   ├── rules/           # codingengine-workflow, quality-standards, context-management
│   └── skills/
│       ├── simplerig/   # 主工作流 Skill
│       └── code-simplifier/  # 代码清理 Skill
├── simplerig/           # 编排引擎（事件溯源、DAG、断点续传）
│   ├── simplerig/
│   │   ├── planner.py   # 按 context_limit 拆分
│   │   ├── runner.py    # 阶段机
│   │   ├── git_ops.py   # 原子提交/回滚
│   │   └── stages.py    # plan/develop/verify/integrate
│   └── config.yaml      # 模型配置（仅 context_limit）
├── docs/
│   └── wiki/            # 文档集
└── AGENTS.md            # 本文件
```

## 关键约定

- **任务拆分**：仅用 `context_limit`，已废弃 `performance_degradation_point`、`optimal_context`
- **原子提交**：每个 task 完成后 `git commit -m "[simplerig] <task_id>"`
- **回滚策略**：失败时 `git revert`
- **工作流**：plan → develop（每 task：修改→lint→code-simplifier→commit）→ verify → 完成

## 参考项目

- simplerig（编排骨架）
- everything-claude-code（ECC agents/skills）
- oh-my-opencode（OMO 3 层委派、Boulder 续航）
- Anthropic code-simplifier（代码清理）
