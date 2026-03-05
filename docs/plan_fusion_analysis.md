# 两个 CodingEngine 计划的融合分析

## 一、两计划核心差异

| 维度 | Plan 1 (Product Plan) | Plan 2 (Revised Plan) |
|------|----------------------|------------------------|
| **编排骨架** | 无 simplerig，Fork ECC 结构自建 | simplerig（事件溯源 + DAG + 断点续传） |
| **Agent 层** | 14 个显式 Agent 定义（strategist, conductor, coder...） | 无，Skill 驱动 Cursor 内置 agent |
| **Skill 数量** | 60+（SWE-bench、编排、OpenSpec、ECC 领域） | 2（simplerig + code-simplifier） |
| **Hook 层** | 有，ECC adapter.js + 7 个 hook | 无，Rules 代替 |
| **Rules** | 4 个（constitution, orchestration, quality, context） | 3 个（workflow, quality, context） |
| **技术栈** | TypeScript + Node.js | Python（simplerig）+ 配置 |
| **原子提交** | 未提及 | 有，git_ops |
| **规划结构** | OpenSpec artifact graph | simplerig plan.json + DAG |
| **复杂度** | 高 | 低 |

---

## 二、用户已确认的约束（来自前期对话）

- **Skill 即胶水**（Route A）— SKILL.md 为唯一集成点
- **simplerig 为基座** — 不从零造轮子
- **控制复杂度** — 不建 14 Agent、60+ Skill、Hook 适配层
- **Cursor only**

→ **Plan 2 的架构选择与用户约束一致**，应作为融合后的主骨架。

---

## 三、Plan 1 中值得保留并融入的内容

### 3.1 战略层（直接并入）

| 内容 | 来源 | 融入方式 |
|------|------|----------|
| 能力分解与提升路径表 | Plan 1 §2.2 | 作为「预期提升路径」的补充，保留 5 维度 + 基准映射 |
| 评估框架（主基准、代码生成、算法、真实项目、质量指标） | Plan 1 §2.3 | 并入 Plan 2 的「评估方式」 |
| 风险与缓解 | Plan 1 §7 | 作为独立章节加入融合计划 |
| 创新点表述 | Plan 1 §4 | 精简后保留（Cascade、Static Context、Feedback、Wisdom、Benchmark-Driven） |

### 3.2 概念层（映射到 Plan 2 架构）

| Plan 1 概念 | 在 Plan 2 中的对应 |
|-------------|---------------------|
| Strategist Agent | simplerig plan 阶段 + SKILL 中的规划指令 |
| Conductor Agent | simplerig DAG scheduler + SKILL 中的委派指令 |
| Coder/Debugger/Tester | Cursor 执行 develop 时的行为，由 SKILL + Rules 引导 |
| Code Reviewer | code-simplifier + quality-standards rule |
| 3 层编排 | plan → develop（并行）→ verify，由 simplerig 阶段机实现 |
| OpenSpec artifact graph | simplerig plan.json 的 dependencies + decoupled 字段 |
| ECC 质量 Hook | quality-standards.mdc + SKILL 中的「编辑后立即 lint」 |
| OMO Boulder 续航 | SKILL 中的「任务未完成不结束 turn」 |
| Wisdom 积累 | SKILL 中的 wisdom.jsonl 写入指令 |

### 3.3 可选的轻量扩展（按需引入）

| Plan 1 内容 | 融入策略 |
|-------------|----------|
| SWE-bench 专项 Skill（swe-issue-analysis 等） | 不建独立 Skill，将其核心逻辑**提炼为段落**写入 simplerig SKILL.md 的 plan/develop 阶段 |
| ECC 58 个领域 Skill | 不全部引入；仅当项目需要时，从 ECC 复制 1–2 个（如 tdd-workflow）到 .cursor/skills/ |
| 4 个 Rules vs 3 个 | 融合后保留 3 个，将 constitution 的要点并入 workflow |
| agents/ 目录 | 不建；Agent 角色由 SKILL 自然语言描述即可 |

### 3.4 明确不融入的内容

| 内容 | 原因 |
|------|------|
| 14 个 Agent 定义文件 | 与「Skill 即胶水」冲突，增加维护成本 |
| 60+ Skill 目录 | 过度复杂，用户明确不建 |
| ECC hooks/adapter.js | 用户选择 Rules 代替 Hook |
| package.json + TypeScript 工具链 | simplerig 为 Python，无需 Node 层 |
| OpenSpec 完整集成 | simplerig plan.json 已覆盖任务依赖，不引入 OpenSpec CLI |

---

## 四、融合后的计划结构建议

```
融合计划 = Plan 2 骨架 + Plan 1 战略补充
```

**保留 Plan 2 的：**
- 以 simplerig 为编排骨架
- Skill 即胶水（simplerig + code-simplifier）
- 3 个 Rules
- 参数化（context_limit）、git_ops、原子提交
- 不做 Agent 层、Hook 层、60+ Skill

**从 Plan 1 补充的：**
- 能力分解与提升路径表（带基准映射）
- 评估框架（5 类基准）
- 风险与缓解
- 创新点（精简版）
- 概念映射说明（Plan 1 的 Agent/概念 → Plan 2 的 SKILL/Rules 实现）

**融合后的目录结构**（与 Plan 2 一致，微调）：

```
CursorCodingEngine/
├── .cursor/
│   ├── rules/
│   │   ├── codingengine-workflow.mdc   # 含 constitution 要点
│   │   ├── quality-standards.mdc
│   │   └── context-management.mdc
│   └── skills/
│       ├── simplerig/SKILL.md
│       └── code-simplifier/SKILL.md
├── simplerig/
├── docs/
│   ├── plan_fusion_analysis.md         # 本文件
│   ├── architecture.md                 # 融合后的架构说明
│   └── decisions/                      # ADR（可选）
├── AGENTS.md
├── config.yaml
└── [参考项目]
```

---

## 五、融合后的 Todo 合并

| 来源 | Todo | 融合后 |
|------|------|--------|
| P2 | clone-simplerig | 保留 |
| P2 | param-config | 保留 |
| P2 | enhance-planner | 保留 |
| P2 | add-git-ops | 保留 |
| P2 | enhance-runner | 保留 |
| P2 | upgrade-skill | 保留（含 Plan 1 的 SWE-bench/OMO/ECC 逻辑提炼） |
| P2 | glue-code-simplifier | 保留 |
| P2 | replace-rules | 保留 |
| P2 | create-agents-md | 保留 |
| P2 | manual-test | 保留 |
| P1 | phase0-scaffold | 精简为「创建 docs/、AGENTS.md」（无 package.json） |
| P1 | phase1-agents | **取消** — 不建 Agent 层 |
| P1 | phase2-skills | **取消** — 不建 60+ Skill，逻辑并入 simplerig SKILL |
| P1 | phase3-hooks | **取消** — 不建 Hook 层 |
| P1 | phase4-eval | 合并入 manual-test，扩展为「手工测试 → SWE-bench 自动化」 |
| P1 | innovation-* | 作为文档记录，不单独 todo |

---

## 六、结论

- **主骨架**：Plan 2
- **战略与评估**：从 Plan 1 补充能力表、评估框架、风险、创新点
- **概念映射**：Plan 1 的 Agent/概念通过 SKILL + Rules 实现，不建独立 Agent 文件
- **不融入**：14 Agent、60+ Skill、Hook 层、TypeScript 工具链

建议将本分析作为输入，生成一份**融合后的单一计划文件**，替代当前两个计划。
