# 参考项目与引用

CodingEngine 是在四个参考项目基础上胶水而成的产品。本节详细说明各项目的定位、贡献及在 CodingEngine 中的融入方式。

---

## 一、simplerig

### 项目定位

simplerig 是基于 **Event Sourcing（事件溯源）** 的多阶段工作流框架。LLM 由编辑器（Cursor / OpenCode）提供，simplerig 负责**事件记录、产物管理、断点续传与可观测性**。

### 核心机制

- **事件溯源**：`events.jsonl` 为事实源，每行一个事件，可重建 Run 状态、审计、统计
- **阶段机**：plan → develop → verify → integrate，按顺序执行并写入 `stage.*` 事件
- **DAG 调度**：任务依赖图，PENDING → READY → RUNNING → COMPLETED/FAILED，支持并行
- **断点续传**：`--resume`、`--from-stage`，重读 events 重建状态后继续
- **产物管理**：plan.json、code_changes.json、verify_result.json 等，带 SHA256 校验

### 在 CodingEngine 中的融入

| simplerig 能力 | CodingEngine 实现 |
|----------------|-------------------|
| init/emit 事件记录 | `codingengine init`、`codingengine emit` |
| 阶段机 | plan → develop → verify → 完成 |
| DAG 调度 | planner 产出 plan.json，runner 按 dependencies 执行 |
| 断点续传 | `codingengine run --resume`、`--from-stage` |
| 产物目录 | `~/.codingengine/runs/<run_id>/artifacts/` |
| 事件流 | `codingengine tail --follow`、`codingengine status` |

CodingEngine 参考 simplerig 设计，**独立实现**，不依赖 simplerig 包。数据目录改为 `~/.codingengine/`，不污染项目目录。

---

## 二、oh-my-opencode (OMO)

### 项目定位

OMO 提供 3 层委派、执行纪律与续航机制，强调 Agent 在开发过程中**少问多做、持续推进**。

### 核心模式

- **"Do NOT Ask — Just Do"**：执行阶段遇到不确定时用最佳判断继续，不因小问题中断；仅在 MT4/图形界面人工验证、业务决策需拍板、外部权限/数据缺失时，才进入等待人工
- **Boulder 续航**：任务未完成不得停；若 session idle 且还有未完成 todo，注入 continuation prompt 继续执行；不因「需要用户确认」而轻易停下
- **Wisdom 积累**：每个任务完成后可提取 learnings，写入 `wisdom.jsonl`，后续任务可引用

### 在 CodingEngine 中的融入

| OMO 模式 | 融入位置 |
|----------|----------|
| Just Do | 主工作流 Skill develop 阶段：「执行阶段禁止向用户提问」 |
| Boulder 续航 | 主工作流 Skill：「任务未完成不得停」「不因需要用户确认而轻易停下」 |
| Wisdom 积累 | verify 阶段通过后，可选写入 `~/.codingengine/runs/<run_id>/artifacts/wisdom.jsonl` |

---

## 三、everything-claude-code (ECC)

### 项目定位

ECC 提供大量 Agent 定义与 Skill，以及质量门禁、置信度审查等机制。

### 核心模式

- **编辑后立即 lint**：每次文件修改后立即跑 lint，不攒到最后
- **Confidence-Based Review**：只报 >80% 确信的问题，减少噪音
- **Severity 分级**：CRITICAL 阻塞，HIGH/MEDIUM/LOW 记录但不阻塞

### 在 CodingEngine 中的融入

| ECC 模式 | 融入位置 |
|----------|----------|
| 编辑后立即 lint | quality-standards.mdc、主工作流 Skill「每个 task：修改 → 立即 lint」 |
| Confidence-Based Review | 主工作流 Skill 质量门禁段落 |
| Severity 分级 | 主工作流 Skill「CRITICAL 阻塞，HIGH/MEDIUM/LOW 记录但不阻塞」 |

CodingEngine 不引入 ECC 的 58+ 领域 Skill 或 Hook 适配层，仅提炼上述模式到 Rules 与主工作流 Skill。

---

## 四、OpenSpec

### 项目定位

OpenSpec 提供 Artifact 依赖图与任务解耦模型，用于表达任务间的依赖与模块边界。

### 核心概念

- **Artifact 依赖图**：任务产出物之间的依赖关系
- **模块解耦**：任务按模块边界拆分，减少跨模块修改

### 在 CodingEngine 中的融入

| OpenSpec 概念 | 融入位置 |
|---------------|----------|
| 任务依赖 | plan.json 的 `dependencies` 字段，DAG 调度依据 |
| 模块解耦 | plan.json 的 `decoupled` 字段，planner 拆分时考虑模块边界 |

CodingEngine 不引入 OpenSpec CLI，plan.json 结构已覆盖任务依赖与解耦需求。

---

## 五、Anthropic code-simplifier

### 项目定位

Anthropic 官方 code-simplifier 插件，用于在保持功能的前提下简化代码、提升可读性。

### 核心原则

1. **Preserve Functionality** — 不改变行为
2. **Apply Project Standards** — 遵循 CLAUDE.md/AGENTS.md
3. **Enhance Clarity** — 减少嵌套、改进命名
4. **Avoid Over-Simplification** — 不牺牲可读性
5. **Focus on Recently Modified** — 仅处理本次修改部分

### 在 CodingEngine 中的融入

转为 Cursor Skill（`.cursor/skills/code-simplifier/SKILL.md`），在 develop 阶段每个 task 提交前调用。泛化语言栈，不限定 ES/React。

---

## 六、其他引用

- **SWE-bench** — 评测基准，目标 50% → 70-80%+
- **HumanEval**、**MBPP** — 代码生成基准
- **RULER benchmark** (NVIDIA 2024) — 长上下文性能研究

---

## 说明

本仓库中的 `simplerig`、`everything-claude-code`、`oh-my-opencode`、`OpenSpec` 为参考文件夹，非项目依赖，不参与安装与运行。
